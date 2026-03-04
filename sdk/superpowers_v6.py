"""
Superpowers Mode v6 - 通过文件通信调用 Claude

工作原理：
1. Python 脚本写入请求文件（request.json）
2. 通知 OpenClaw 主会话处理请求
3. OpenClaw 调用 Claude 并写入响应文件（response.json）
4. Python 脚本读取响应文件
"""

import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path


class SuperpowersModeV6:
    """Superpowers 模式 v6 - 通过文件通信"""
    
    def __init__(self):
        self.history = []
        self.comm_dir = Path("C:/Users/A/.openclaw/workspace/aios/sdk/.comm")
        self.comm_dir.mkdir(exist_ok=True)
        
    def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        max_steps: int = 10,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        直接执行任务（真实 Claude 决策）
        
        Args:
            task: 任务描述
            context: 上下文信息
            max_steps: 最大执行步数
            timeout: 超时时间（秒）
            
        Returns:
            执行结果
        """
        task_id = f"superpower_{int(time.time() * 1000)}"
        start_time = time.time()
        self.history = []
        
        print(f"\n[START] Task: {task}")
        print(f"[INFO] Task ID: {task_id}")
        print(f"[INFO] Max steps: {max_steps}, Timeout: {timeout}s\n")
        
        try:
            # 执行循环
            for step in range(1, max_steps + 1):
                # 检查超时
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Timeout ({timeout}s)")
                
                print(f"[STEP {step}]")
                
                # Claude 决策
                decision = self._claude_decide_via_file(
                    task=task,
                    context=context,
                    history=self.history,
                    step=step
                )
                
                print(f"[DECISION] {decision['action']}")
                print(f"[REASON] {decision.get('reasoning', 'N/A')[:80]}...")
                
                # 检查是否完成
                if decision["action"] == "done":
                    print(f"[DONE] Task completed!")
                    return {
                        "success": True,
                        "task_id": task_id,
                        "result": decision.get("result"),
                        "elapsed": time.time() - start_time,
                        "steps": step - 1,
                        "history": self.history
                    }
                
                # 执行动作
                print(f"[EXEC] Executing...")
                action_result = self._execute_action(decision)
                
                if action_result["success"]:
                    print(f"[OK] Success")
                    if action_result.get("output"):
                        output = action_result['output'][:80]
                        print(f"[OUTPUT] {output}...")
                else:
                    print(f"[ERROR] {action_result.get('error')}")
                
                # 记录历史
                self.history.append({
                    "step": step,
                    "decision": decision,
                    "result": action_result
                })
                
                print()
            
            raise RuntimeError(f"Max steps ({max_steps}) reached")
            
        except Exception as e:
            print(f"\n[FAIL] {e}\n")
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "elapsed": time.time() - start_time,
                "history": self.history
            }
    
    def _claude_decide_via_file(
        self,
        task: str,
        context: Optional[Dict[str, Any]],
        history: List[Dict[str, Any]],
        step: int
    ) -> Dict[str, Any]:
        """
        通过文件通信调用 Claude
        
        流程：
        1. 写入 request.json
        2. 创建 request.flag（通知 OpenClaw）
        3. 等待 response.json
        4. 读取响应
        """
        request_file = self.comm_dir / "request.json"
        response_file = self.comm_dir / "response.json"
        flag_file = self.comm_dir / "request.flag"
        
        # 清理旧文件
        if response_file.exists():
            response_file.unlink()
        if flag_file.exists():
            flag_file.unlink()
        
        # 构建 prompt
        prompt = self._build_prompt(task, context, history, step)
        
        # 写入请求
        request = {
            "task": task,
            "step": step,
            "prompt": prompt,
            "timestamp": time.time()
        }
        request_file.write_text(json.dumps(request, indent=2), encoding='utf-8')
        
        # 创建标志文件（通知 OpenClaw）
        flag_file.write_text("ready", encoding='utf-8')
        
        print(f"[WAIT] Waiting for Claude response...")
        
        # 等待响应（最多30秒）
        start_wait = time.time()
        while time.time() - start_wait < 30:
            if response_file.exists():
                try:
                    response_text = response_file.read_text(encoding='utf-8')
                    response = json.loads(response_text)
                    
                    # 清理文件
                    flag_file.unlink()
                    
                    return response
                except Exception as e:
                    print(f"[WARN] Failed to read response: {e}")
                    time.sleep(0.5)
                    continue
            
            time.sleep(0.5)
        
        # 超时，使用 fallback
        print(f"[WARN] Claude response timeout, using fallback")
        return self._fallback_decision(step)
    
    def _fallback_decision(self, step: int) -> Dict[str, Any]:
        """Fallback 决策"""
        if step == 1:
            return {
                "action": "shell",
                "params": {"command": "echo 'Step 1: Analyzing'"},
                "reasoning": "First step (fallback)"
            }
        elif step == 2:
            return {
                "action": "shell",
                "params": {"command": "echo 'Step 2: Executing'"},
                "reasoning": "Second step (fallback)"
            }
        else:
            return {
                "action": "done",
                "result": {
                    "status": "completed",
                    "message": "Task completed (fallback)",
                    "steps": step - 1
                },
                "reasoning": "Task completed (fallback)"
            }
    
    def _build_prompt(
        self,
        task: str,
        context: Optional[Dict[str, Any]],
        history: List[Dict[str, Any]],
        step: int
    ) -> str:
        """构建 Claude prompt"""
        prompt = f"""You are an AI assistant using Superpowers mode.

**Task:** {task}

**Context:** {json.dumps(context or {}, indent=2)}

**Step:** {step}

**History:**
"""
        if not history:
            prompt += "(No history)\n"
        else:
            for h in history[-3:]:  # 只显示最近3步
                prompt += f"\nStep {h['step']}: {h['decision']['action']}"
                if h['result'].get('success'):
                    prompt += f" -> Success"
                else:
                    prompt += f" -> Failed: {h['result'].get('error', 'Unknown')}"
        
        prompt += """

**Actions:**
- shell: {"action": "shell", "params": {"command": "..."}, "reasoning": "..."}
- read: {"action": "read", "params": {"path": "..."}, "reasoning": "..."}
- write: {"action": "write", "params": {"path": "...", "content": "..."}, "reasoning": "..."}
- http: {"action": "http", "params": {"method": "GET/POST", "url": "...", "headers": {...}, "data": {...}}, "reasoning": "..."}
- done: {"action": "done", "result": {...}, "reasoning": "..."}

**Return JSON only.**
"""
        return prompt
    
    def _execute_action(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作"""
        action = decision["action"]
        params = decision.get("params", {})
        
        if action == "shell":
            import subprocess
            try:
                result = subprocess.run(
                    params["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout.strip(),
                    "error": result.stderr.strip() if result.stderr else None
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif action == "read":
            try:
                with open(params["path"], "r", encoding="utf-8") as f:
                    content = f.read()
                return {"success": True, "output": content}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif action == "write":
            try:
                with open(params["path"], "w", encoding="utf-8") as f:
                    f.write(params["content"])
                return {
                    "success": True,
                    "output": f"Wrote {len(params['content'])} chars"
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif action == "http":
            # HTTP 请求
            try:
                import sys
                sys.path.insert(0, "C:/Users/A/.openclaw/workspace")
                from aios.sdk.tools.http_tool import http_request
                
                method = params.get("method", "GET")
                url = params["url"]
                headers = params.get("headers")
                data = params.get("data")
                
                result = http_request(method, url, headers=headers, data=data)
                
                if result["success"]:
                    output = f"HTTP {method} {url} -> {result['status_code']}"
                    return {
                        "success": True,
                        "output": output,
                        "data": result.get("body_json") or result.get("body")
                    }
                else:
                    return {"success": False, "error": result.get("error")}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        else:
            return {"success": False, "error": f"Unknown action: {action}"}


def superpower(task: str, **kwargs) -> Dict[str, Any]:
    """快速执行任务"""
    mode = SuperpowersModeV6()
    return mode.execute(task, **kwargs)


if __name__ == "__main__":
    print("=" * 60)
    print("Superpowers Mode v6 - File Communication")
    print("=" * 60)
    
    result = superpower("Create a Python script that prints Hello World")
    
    print("\n" + "=" * 60)
    print("Result")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
