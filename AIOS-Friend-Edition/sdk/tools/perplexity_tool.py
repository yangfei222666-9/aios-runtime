"""
Perplexity Search Tool for Superpowers Mode

集成 Perplexity API 进行实时搜索
"""

import json
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path


def perplexity_search(
    query: str,
    count: int = 5,
    model: str = "sonar-pro",
    timeout: int = 60
) -> Dict[str, Any]:
    """
    使用 Perplexity 搜索
    
    Args:
        query: 搜索查询
        count: 结果数量（1-10）
        model: 模型（sonar-pro/sonar/sonar-reasoning）
        timeout: 超时时间（秒）
        
    Returns:
        搜索结果
    """
    try:
        # Perplexity skill 路径
        skill_dir = Path("C:/Users/A/.openclaw/workspace/skills/perplexity-search")
        script = skill_dir / "scripts" / "search.mjs"
        
        if not script.exists():
            return {
                "success": False,
                "error": "Perplexity skill not found"
            }
        
        # 执行搜索
        cmd = [
            "node",
            str(script),
            query,
            "-n", str(count),
            "--model", model,
            "--json"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(skill_dir)
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr or "Search failed"
            }
        
        # 解析结果
        try:
            data = json.loads(result.stdout)
            return {
                "success": True,
                "query": query,
                "answer": data.get("answer", ""),
                "sources": data.get("sources", []),
                "model": model
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response"
            }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Search timeout ({timeout}s)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def perplexity_ask(
    question: str,
    context: Optional[str] = None,
    model: str = "sonar-pro",
    timeout: int = 60
) -> Dict[str, Any]:
    """
    对话式搜索（带上下文）
    
    Args:
        question: 问题
        context: 上下文
        model: 模型
        timeout: 超时时间（秒）
        
    Returns:
        回答结果
    """
    try:
        skill_dir = Path("C:/Users/A/.openclaw/workspace/skills/perplexity-search")
        script = skill_dir / "scripts" / "ask.mjs"
        
        if not script.exists():
            return {
                "success": False,
                "error": "Perplexity skill not found"
            }
        
        cmd = [
            "node",
            str(script),
            question,
            "--model", model,
            "--json"
        ]
        
        if context:
            cmd.extend(["--context", context])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(skill_dir)
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr or "Ask failed"
            }
        
        try:
            data = json.loads(result.stdout)
            return {
                "success": True,
                "question": question,
                "answer": data.get("answer", ""),
                "sources": data.get("sources", []),
                "model": model
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response"
            }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Ask timeout ({timeout}s)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # 测试
    print("Testing Perplexity search...")
    
    # 测试搜索
    result = perplexity_search("latest AIOS projects on GitHub", count=3)
    print(f"\nSearch test:")
    print(f"  Success: {result['success']}")
    if result['success']:
        print(f"  Query: {result['query']}")
        print(f"  Answer: {result['answer'][:200]}...")
        print(f"  Sources: {len(result['sources'])} sources")
    else:
        print(f"  Error: {result['error']}")
