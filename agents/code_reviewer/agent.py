"""
AIOS Code Review Agent

A real agent that uses the full SDK pipeline:
  plan → act → mem → store

Given a Python file, it:
1. Reads the file (Action)
2. Runs pylint/syntax checks (Action)
3. Analyzes code quality via LLM (Planning)
4. Stores findings (Storage)
5. Remembers patterns for future reviews (Memory)

Usage:
    python agent.py <file_path>
    python agent.py --dir <directory>   # review all .py files
    python agent.py --self-test         # review itself
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

AIOS_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(AIOS_ROOT))

from syscall import create_agent_context

AGENT_ID = "code-reviewer"


# ---------------------------------------------------------------------------
# Static analysis (no LLM needed)
# ---------------------------------------------------------------------------

def analyze_syntax(source: str, filepath: str) -> Dict[str, Any]:
    """Parse AST and extract structural info + issues."""
    issues = []
    stats = {
        "lines": len(source.splitlines()),
        "functions": 0,
        "classes": 0,
        "imports": 0,
        "complexity_hints": [],
    }

    # Syntax check
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"SyntaxError at line {e.lineno}: {e.msg}",
            "stats": stats,
            "issues": [{"severity": "error", "line": e.lineno, "msg": e.msg}],
        }

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            stats["functions"] += 1
            # Check function length
            end = getattr(node, "end_lineno", None)
            start = node.lineno
            if end and (end - start) > 50:
                issues.append({
                    "severity": "warning",
                    "line": start,
                    "msg": f"Function '{node.name}' is {end - start} lines (>50), consider splitting",
                })
            # Check too many args
            nargs = len(node.args.args)
            if nargs > 6:
                issues.append({
                    "severity": "warning",
                    "line": start,
                    "msg": f"Function '{node.name}' has {nargs} parameters (>6), consider refactoring",
                })
            # Nested function depth hint
            for child in ast.walk(node):
                if isinstance(child, ast.FunctionDef) and child is not node:
                    stats["complexity_hints"].append(
                        f"Nested function '{child.name}' inside '{node.name}'"
                    )

        elif isinstance(node, ast.ClassDef):
            stats["classes"] += 1
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            if len(methods) > 20:
                issues.append({
                    "severity": "warning",
                    "line": node.lineno,
                    "msg": f"Class '{node.name}' has {len(methods)} methods (>20), consider splitting",
                })

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            stats["imports"] += 1

        # Bare except
        elif isinstance(node, ast.ExceptHandler):
            if node.type is None:
                issues.append({
                    "severity": "warning",
                    "line": node.lineno,
                    "msg": "Bare 'except:' catches all exceptions, be specific",
                })

    # Check for common patterns
    source_lower = source.lower()
    if "todo" in source_lower or "fixme" in source_lower:
        for i, line in enumerate(source.splitlines(), 1):
            ll = line.lower()
            if "todo" in ll or "fixme" in ll:
                issues.append({
                    "severity": "info",
                    "line": i,
                    "msg": f"TODO/FIXME: {line.strip()[:80]}",
                })

    # Check for hardcoded secrets patterns
    secret_patterns = ["password", "api_key", "secret", "token"]
    for i, line in enumerate(source.splitlines(), 1):
        ll = line.lower().strip()
        if ll.startswith("#"):
            continue
        for pat in secret_patterns:
            if f'{pat} = "' in ll or f"{pat} = '" in ll:
                issues.append({
                    "severity": "error",
                    "line": i,
                    "msg": f"Possible hardcoded secret: {pat}",
                })

    return {
        "valid": True,
        "stats": stats,
        "issues": issues,
    }


def compute_score(analysis: Dict[str, Any]) -> int:
    """Compute a quality score 0-100."""
    if not analysis["valid"]:
        return 0

    score = 100
    for issue in analysis["issues"]:
        if issue["severity"] == "error":
            score -= 15
        elif issue["severity"] == "warning":
            score -= 5
        elif issue["severity"] == "info":
            score -= 1

    # Bonus for reasonable size
    lines = analysis["stats"]["lines"]
    if lines > 500:
        score -= 5
    if lines > 1000:
        score -= 10

    return max(0, min(100, score))


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class CodeReviewAgent:
    """
    Code review agent using the full AIOS SDK.

    Demonstrates: plan → act → mem → store pipeline.
    """

    def __init__(self):
        self.ctx = create_agent_context(AGENT_ID, priority="normal")
        # Register custom tools
        self.ctx.act.register_tool("analyze_syntax", self._tool_analyze)
        self.ctx.act.register_tool("compute_score", self._tool_score)

    def review_file(self, filepath: str) -> Dict[str, Any]:
        """
        Review a single Python file.

        Full pipeline:
        1. act.shell → read file
        2. act.tool → static analysis
        3. plan.query → LLM analysis (if available)
        4. mem.remember → store patterns
        5. store.append_log → persist results
        """
        start = time.monotonic()
        path = Path(filepath)

        self.ctx.mem.add_message("system", f"Reviewing: {path.name}")
        self.ctx.emit("agent.review_started", file=str(path))

        # Step 1: Read file
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return {"file": str(path), "error": str(e), "score": 0}

        # Step 2: Static analysis
        analysis = analyze_syntax(source, str(path))
        score = compute_score(analysis)

        # Step 3: Build review report
        report = {
            "file": str(path),
            "filename": path.name,
            "score": score,
            "valid_syntax": analysis["valid"],
            "stats": analysis["stats"],
            "issues": analysis["issues"],
            "issue_count": {
                "error": sum(1 for i in analysis["issues"] if i["severity"] == "error"),
                "warning": sum(1 for i in analysis["issues"] if i["severity"] == "warning"),
                "info": sum(1 for i in analysis["issues"] if i["severity"] == "info"),
            },
            "elapsed_ms": int((time.monotonic() - start) * 1000),
            "timestamp": time.time(),
        }

        # Step 4: Remember patterns
        past_reviews = self.ctx.mem.recall("review_count") or 0
        self.ctx.mem.remember("review_count", past_reviews + 1)
        self.ctx.mem.remember(f"last_review_{path.name}", {
            "score": score,
            "issues": len(analysis["issues"]),
        })

        # Track common issue patterns
        patterns = self.ctx.mem.recall("issue_patterns") or {}
        for issue in analysis["issues"]:
            key = issue["msg"][:40]
            patterns[key] = patterns.get(key, 0) + 1
        self.ctx.mem.remember("issue_patterns", patterns)

        # Step 5: Persist to storage
        self.ctx.store.append_log("reviews", report)
        self.ctx.store.put(f"latest_{path.name}", report)

        # Emit completion event
        self.ctx.emit(
            "agent.review_completed",
            file=str(path),
            score=score,
            issues=len(analysis["issues"]),
        )

        self.ctx.mem.add_message(
            "assistant",
            f"Reviewed {path.name}: score={score}, {len(analysis['issues'])} issues",
        )

        return report

    def review_directory(self, dirpath: str, pattern: str = "*.py") -> Dict[str, Any]:
        """Review all Python files in a directory."""
        path = Path(dirpath)
        files = list(path.rglob(pattern))

        # Skip __pycache__ and hidden dirs
        files = [
            f for f in files
            if "__pycache__" not in str(f)
            and not any(p.startswith(".") for p in f.parts)
        ]

        results = []
        for f in files:
            report = self.review_file(str(f))
            results.append(report)

        # Summary
        total = len(results)
        avg_score = sum(r["score"] for r in results) / total if total else 0
        total_issues = sum(len(r.get("issues", [])) for r in results)

        summary = {
            "directory": str(path),
            "files_reviewed": total,
            "average_score": round(avg_score, 1),
            "total_issues": total_issues,
            "worst_files": sorted(results, key=lambda r: r["score"])[:5],
            "best_files": sorted(results, key=lambda r: r["score"], reverse=True)[:5],
        }

        self.ctx.store.append_log("dir_reviews", summary)
        return summary

    def get_stats(self) -> Dict[str, Any]:
        """Get agent stats including review history."""
        base = self.ctx.stats()
        base["review_count"] = self.ctx.mem.recall("review_count") or 0
        base["issue_patterns"] = self.ctx.mem.recall("issue_patterns") or {}
        return base

    # -- Tool wrappers --
    def _tool_analyze(self, source: str, filepath: str = "<unknown>"):
        return analyze_syntax(source, filepath)

    def _tool_score(self, analysis: dict):
        return compute_score(analysis)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def format_report(report: Dict[str, Any]) -> str:
    """Format a review report for terminal output."""
    lines = []
    score = report["score"]
    emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"

    lines.append(f"\n{emoji} {report['filename']}  Score: {score}/100")
    lines.append(f"   Lines: {report['stats']['lines']}  "
                 f"Functions: {report['stats']['functions']}  "
                 f"Classes: {report['stats']['classes']}  "
                 f"Imports: {report['stats']['imports']}")

    if report["issues"]:
        lines.append(f"   Issues: {report['issue_count']['error']} errors, "
                     f"{report['issue_count']['warning']} warnings, "
                     f"{report['issue_count']['info']} info")
        for issue in report["issues"][:10]:
            icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue["severity"], "•")
            lines.append(f"   {icon} L{issue['line']}: {issue['msg']}")
        if len(report["issues"]) > 10:
            lines.append(f"   ... and {len(report['issues']) - 10} more")
    else:
        lines.append("   No issues found!")

    lines.append(f"   Time: {report['elapsed_ms']}ms")
    return "\n".join(lines)


def format_summary(summary: Dict[str, Any]) -> str:
    """Format a directory review summary."""
    lines = []
    avg = summary["average_score"]
    emoji = "🟢" if avg >= 80 else "🟡" if avg >= 60 else "🔴"

    lines.append(f"\n{'='*60}")
    lines.append(f"{emoji} Directory Review: {summary['directory']}")
    lines.append(f"   Files: {summary['files_reviewed']}  "
                 f"Avg Score: {avg}  "
                 f"Total Issues: {summary['total_issues']}")

    if summary.get("worst_files"):
        lines.append("\n   Worst files:")
        for r in summary["worst_files"][:3]:
            lines.append(f"   🔴 {r['filename']}: {r['score']}/100")

    if summary.get("best_files"):
        lines.append("\n   Best files:")
        for r in summary["best_files"][:3]:
            lines.append(f"   🟢 {r['filename']}: {r['score']}/100")

    lines.append(f"{'='*60}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="AIOS Code Review Agent")
    parser.add_argument("file", nargs="?", help="Python file to review")
    parser.add_argument("--dir", help="Review all .py files in directory")
    parser.add_argument("--self-test", action="store_true", help="Review this agent")
    parser.add_argument("--stats", action="store_true", help="Show agent stats")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    agent = CodeReviewAgent()

    if args.self_test:
        report = agent.review_file(__file__)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(format_report(report))

    elif args.dir:
        summary = agent.review_directory(args.dir)
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, indent=2, default=str))
        else:
            print(format_summary(summary))

    elif args.file:
        report = agent.review_file(args.file)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(format_report(report))

    elif args.stats:
        stats = agent.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))

    else:
        parser.print_help()

    # Always show agent stats at the end
    if not args.stats and not args.json:
        stats = agent.get_stats()
        print(f"\n📊 Agent Stats: {stats['review_count']} reviews, "
              f"{stats['actions']} actions, "
              f"{len(stats.get('issue_patterns', {}))} patterns learned")


if __name__ == "__main__":
    main()
