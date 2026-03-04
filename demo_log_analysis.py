"""
AIOS Demo: Log Analysis + Auto Playbook Generation

Real-world scenario: Analyze error logs and automatically generate fix playbooks.

Scenario:
1. Monitor error logs
2. Detect error patterns (same error repeated)
3. Analyze error context (stack trace, frequency, etc.)
4. Auto-generate fix playbook (steps to resolve)
5. Apply playbook automatically (if safe)

This demonstrates:
- Pattern recognition
- Root cause analysis
- Auto-remediation
- Knowledge accumulation
"""
import sys
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import Counter
from datetime import datetime

# Add AIOS to path
AIOS_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(AIOS_ROOT))


@dataclass
class LogEntry:
    """A log entry."""
    timestamp: str
    level: str
    message: str
    context: Dict[str, any]


@dataclass
class ErrorPattern:
    """An identified error pattern."""
    error_type: str
    message_pattern: str
    occurrences: int
    first_seen: str
    last_seen: str
    contexts: List[Dict[str, any]]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Playbook:
    """A fix playbook."""
    name: str
    error_pattern: str
    steps: List[str]
    risk_level: str  # "low", "medium", "high"
    auto_apply: bool
    created_at: str
    
    def to_dict(self):
        return asdict(self)


class LogAnalyzer:
    """Analyze logs and generate fix playbooks."""
    
    # Known error patterns and their fixes
    KNOWN_PATTERNS = {
        "FileNotFoundError": {
            "pattern": r"FileNotFoundError.*'(.+?)'",
            "playbook": {
                "name": "Create Missing File",
                "steps": [
                    "Check if file path is correct",
                    "Create missing directory if needed",
                    "Create empty file with default content",
                    "Verify file permissions",
                ],
                "risk_level": "low",
                "auto_apply": True,
            }
        },
        "ConnectionError": {
            "pattern": r"ConnectionError.*timeout",
            "playbook": {
                "name": "Retry Connection",
                "steps": [
                    "Check network connectivity",
                    "Verify service is running",
                    "Retry with exponential backoff",
                    "Alert if still failing after 3 retries",
                ],
                "risk_level": "low",
                "auto_apply": True,
            }
        },
        "MemoryError": {
            "pattern": r"MemoryError|Out of memory",
            "playbook": {
                "name": "Free Memory",
                "steps": [
                    "Clear cache",
                    "Garbage collect",
                    "Reduce batch size",
                    "Restart service if needed",
                ],
                "risk_level": "medium",
                "auto_apply": False,
            }
        },
        "PermissionError": {
            "pattern": r"PermissionError.*'(.+?)'",
            "playbook": {
                "name": "Fix Permissions",
                "steps": [
                    "Check current file permissions",
                    "Verify user has required access",
                    "Update permissions if safe",
                    "Alert admin if elevated access needed",
                ],
                "risk_level": "high",
                "auto_apply": False,
            }
        },
    }
    
    def __init__(self, log_file: Path, output_dir: Path):
        self.log_file = log_file
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self._error_patterns: Dict[str, ErrorPattern] = {}
        self._generated_playbooks: List[Playbook] = []
    
    def parse_logs(self) -> List[LogEntry]:
        """Parse log file."""
        entries = []
        
        if not self.log_file.exists():
            return entries
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    data = json.loads(line)
                    entry = LogEntry(
                        timestamp=data.get("timestamp", ""),
                        level=data.get("level", "INFO"),
                        message=data.get("message", ""),
                        context=data.get("context", {}),
                    )
                    entries.append(entry)
                except json.JSONDecodeError:
                    # Skip malformed lines
                    continue
        
        return entries
    
    def analyze_errors(self, entries: List[LogEntry]) -> List[ErrorPattern]:
        """Analyze error patterns."""
        error_entries = [e for e in entries if e.level in ["ERROR", "CRITICAL"]]
        
        if not error_entries:
            return []
        
        # Group by error type
        error_groups: Dict[str, List[LogEntry]] = {}
        
        for entry in error_entries:
            # Extract error type
            error_type = "Unknown"
            for known_type in self.KNOWN_PATTERNS.keys():
                if known_type in entry.message:
                    error_type = known_type
                    break
            
            if error_type not in error_groups:
                error_groups[error_type] = []
            error_groups[error_type].append(entry)
        
        # Create patterns
        patterns = []
        for error_type, group in error_groups.items():
            pattern = ErrorPattern(
                error_type=error_type,
                message_pattern=group[0].message[:100],  # First 100 chars
                occurrences=len(group),
                first_seen=group[0].timestamp,
                last_seen=group[-1].timestamp,
                contexts=[e.context for e in group[:5]],  # First 5 contexts
            )
            patterns.append(pattern)
            self._error_patterns[error_type] = pattern
        
        return patterns
    
    def generate_playbooks(self, patterns: List[ErrorPattern]) -> List[Playbook]:
        """Generate fix playbooks for error patterns."""
        playbooks = []
        
        for pattern in patterns:
            if pattern.error_type in self.KNOWN_PATTERNS:
                template = self.KNOWN_PATTERNS[pattern.error_type]["playbook"]
                
                playbook = Playbook(
                    name=template["name"],
                    error_pattern=pattern.error_type,
                    steps=template["steps"],
                    risk_level=template["risk_level"],
                    auto_apply=template["auto_apply"],
                    created_at=datetime.now().isoformat(),
                )
                
                playbooks.append(playbook)
                self._generated_playbooks.append(playbook)
                
                # Save playbook
                playbook_file = self.output_dir / f"playbook_{pattern.error_type}.json"
                with open(playbook_file, "w", encoding="utf-8") as f:
                    json.dump(playbook.to_dict(), f, indent=2, ensure_ascii=False)
        
        return playbooks
    
    def apply_playbook(self, playbook: Playbook) -> bool:
        """Apply a playbook (simulate)."""
        if not playbook.auto_apply:
            print(f"  ⚠️  Playbook '{playbook.name}' requires manual approval (risk: {playbook.risk_level})")
            return False
        
        print(f"  🔧 Applying playbook: {playbook.name}")
        for i, step in enumerate(playbook.steps, 1):
            print(f"     {i}. {step}")
            time.sleep(0.2)  # Simulate execution
        
        print(f"  ✓ Playbook applied successfully")
        return True
    
    def get_summary(self) -> Dict[str, any]:
        """Get analysis summary."""
        return {
            "total_patterns": len(self._error_patterns),
            "total_playbooks": len(self._generated_playbooks),
            "auto_applied": sum(1 for p in self._generated_playbooks if p.auto_apply),
            "manual_review": sum(1 for p in self._generated_playbooks if not p.auto_apply),
        }


def create_demo_logs(log_file: Path):
    """Create demo log file with various errors."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logs = [
        {"timestamp": "2026-02-27T18:00:01", "level": "INFO", "message": "Application started", "context": {}},
        {"timestamp": "2026-02-27T18:00:05", "level": "ERROR", "message": "FileNotFoundError: [Errno 2] No such file or directory: '/tmp/config.json'", "context": {"file": "/tmp/config.json"}},
        {"timestamp": "2026-02-27T18:00:10", "level": "INFO", "message": "Processing request", "context": {}},
        {"timestamp": "2026-02-27T18:00:15", "level": "ERROR", "message": "ConnectionError: Connection timeout after 5s", "context": {"host": "api.example.com", "timeout": 5}},
        {"timestamp": "2026-02-27T18:00:20", "level": "ERROR", "message": "FileNotFoundError: [Errno 2] No such file or directory: '/tmp/data.csv'", "context": {"file": "/tmp/data.csv"}},
        {"timestamp": "2026-02-27T18:00:25", "level": "WARNING", "message": "Slow query detected", "context": {"duration": 3.5}},
        {"timestamp": "2026-02-27T18:00:30", "level": "ERROR", "message": "MemoryError: Out of memory", "context": {"allocated": "8GB", "requested": "2GB"}},
        {"timestamp": "2026-02-27T18:00:35", "level": "ERROR", "message": "ConnectionError: Connection timeout after 5s", "context": {"host": "db.example.com", "timeout": 5}},
        {"timestamp": "2026-02-27T18:00:40", "level": "ERROR", "message": "PermissionError: [Errno 13] Permission denied: '/var/log/app.log'", "context": {"file": "/var/log/app.log"}},
        {"timestamp": "2026-02-27T18:00:45", "level": "INFO", "message": "Request completed", "context": {}},
    ]
    
    with open(log_file, "w", encoding="utf-8") as f:
        for log in logs:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")
    
    print(f"[Demo] Created log file with {len(logs)} entries")


def main():
    """Run the demo."""
    print("=" * 70)
    print("AIOS Demo: Log Analysis + Auto Playbook Generation")
    print("=" * 70)
    print("\nScenario:")
    print("  1. Monitor error logs")
    print("  2. Detect error patterns (same error repeated)")
    print("  3. Analyze error context (stack trace, frequency, etc.)")
    print("  4. Auto-generate fix playbook (steps to resolve)")
    print("  5. Apply playbook automatically (if safe)")
    print("\nThis demonstrates:")
    print("  - Pattern recognition")
    print("  - Root cause analysis")
    print("  - Auto-remediation")
    print("  - Knowledge accumulation")
    print("=" * 70)
    
    # Setup
    demo_dir = AIOS_ROOT / "demo_data" / "log_analysis"
    log_file = demo_dir / "app.log"
    playbook_dir = demo_dir / "playbooks"
    
    # Clean up previous demo
    if demo_dir.exists():
        import shutil
        shutil.rmtree(demo_dir)
    
    # Create demo logs
    create_demo_logs(log_file)
    
    # Initialize analyzer
    analyzer = LogAnalyzer(log_file, playbook_dir)
    
    print(f"\n[Setup] Analyzer initialized")
    print(f"  Log file: {log_file}")
    print(f"  Playbook dir: {playbook_dir}")
    
    # Parse logs
    print("\n" + "=" * 70)
    print("Step 1: Parse Logs")
    print("=" * 70)
    
    entries = analyzer.parse_logs()
    print(f"\nParsed {len(entries)} log entries")
    
    error_count = sum(1 for e in entries if e.level in ["ERROR", "CRITICAL"])
    warning_count = sum(1 for e in entries if e.level == "WARNING")
    info_count = sum(1 for e in entries if e.level == "INFO")
    
    print(f"  ERROR/CRITICAL: {error_count}")
    print(f"  WARNING: {warning_count}")
    print(f"  INFO: {info_count}")
    
    # Analyze errors
    print("\n" + "=" * 70)
    print("Step 2: Analyze Error Patterns")
    print("=" * 70)
    
    patterns = analyzer.analyze_errors(entries)
    print(f"\nFound {len(patterns)} error patterns:")
    
    for pattern in patterns:
        print(f"\n  {pattern.error_type}")
        print(f"    Occurrences: {pattern.occurrences}")
        print(f"    First seen: {pattern.first_seen}")
        print(f"    Last seen: {pattern.last_seen}")
    
    # Generate playbooks
    print("\n" + "=" * 70)
    print("Step 3: Generate Fix Playbooks")
    print("=" * 70)
    
    playbooks = analyzer.generate_playbooks(patterns)
    print(f"\nGenerated {len(playbooks)} playbooks:")
    
    for playbook in playbooks:
        print(f"\n  {playbook.name} (for {playbook.error_pattern})")
        print(f"    Risk level: {playbook.risk_level}")
        print(f"    Auto-apply: {playbook.auto_apply}")
        print(f"    Steps:")
        for i, step in enumerate(playbook.steps, 1):
            print(f"      {i}. {step}")
    
    # Apply playbooks
    print("\n" + "=" * 70)
    print("Step 4: Apply Playbooks")
    print("=" * 70)
    
    for playbook in playbooks:
        print(f"\n[Playbook] {playbook.name}")
        analyzer.apply_playbook(playbook)
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary:")
    print("=" * 70)
    
    summary = analyzer.get_summary()
    print(f"\nError patterns detected: {summary['total_patterns']}")
    print(f"Playbooks generated: {summary['total_playbooks']}")
    print(f"  Auto-applied: {summary['auto_applied']}")
    print(f"  Manual review: {summary['manual_review']}")
    
    print("\n" + "=" * 70)
    print("Demo completed! ✓")
    print("=" * 70)
    print(f"\nDemo files saved to: {demo_dir}")
    print("You can inspect the generated playbooks in the playbooks/ folder.")


if __name__ == "__main__":
    main()
