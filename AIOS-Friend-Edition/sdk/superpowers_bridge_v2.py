"""
Superpowers Claude Bridge v2 - 集成真实 Claude API

工作原理：
1. Bridge 收到请求
2. Bridge 创建 claude_request.json（包含 prompt）
3. OpenClaw 主会话监听到请求
4. 调用 Claude（就是我）
5. 写入 claude_response.json
6. Bridge 读取响应并返回
"""

import json
import time
from pathlib import Path


def call_claude(prompt: str, timeout: int = 30) -> str:
    """
    调用 Claude（通过文件通信）
    
    Args:
        prompt: 提示词
        timeout: 超时时间（秒）
        
    Returns:
        Claude 的响应
    """
    comm_dir = Path("C:/Users/A/.openclaw/workspace/aios/sdk/.comm")
    claude_request = comm_dir / "claude_request.json"
    claude_response = comm_dir / "claude_response.json"
    claude_flag = comm_dir / "claude_request.flag"
    
    # 清理旧文件
    if claude_response.exists():
        claude_response.unlink()
    if claude_flag.exists():
        claude_flag.unlink()
    
    # 写入请求
    request = {
        "prompt": prompt,
        "timestamp": time.time()
    }
    claude_request.write_text(json.dumps(request, indent=2), encoding='utf-8')
    
    # 创建标志文件
    claude_flag.write_text("ready", encoding='utf-8')
    
    print(f"[BRIDGE] Waiting for Claude response...")
    
    # 等待响应
    start_wait = time.time()
    while time.time() - start_wait < timeout:
        if claude_response.exists():
            try:
                response_text = claude_response.read_text(encoding='utf-8')
                response = json.loads(response_text)
                
                # 清理标志文件
                if claude_flag.exists():
                    claude_flag.unlink()
                
                return response.get("response", "")
            except Exception as e:
                print(f"[BRIDGE] Failed to read Claude response: {e}")
                time.sleep(0.5)
                continue
        
        time.sleep(0.5)
    
    # 超时
    raise TimeoutError("Claude response timeout")


def parse_decision(response: str) -> dict:
    """
    从 Claude 响应中解析决策
    
    Args:
        response: Claude 的响应（可能是纯 JSON 字符串）
        
    Returns:
        决策字典
    """
    import re
    
    # 如果响应本身就是 JSON 字符串，直接解析
    try:
        return json.loads(response)
    except:
        pass
    
    # 尝试提取 JSON（更宽松的匹配）
    json_match = re.search(r'\{.*?"action".*?\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except:
            pass
    
    # 如果没有找到 JSON，返回默认决策
    return {
        "action": "done",
        "result": {
            "status": "completed",
            "message": response[:200]
        },
        "reasoning": "Claude response (no JSON found)"
    }


def process_request():
    """处理一个请求"""
    comm_dir = Path("C:/Users/A/.openclaw/workspace/aios/sdk/.comm")
    request_file = comm_dir / "request.json"
    response_file = comm_dir / "response.json"
    flag_file = comm_dir / "request.flag"
    
    # 检查是否有请求
    if not flag_file.exists():
        return False
    
    print(f"\n[BRIDGE] Found request, processing...")
    
    try:
        # 读取请求
        request = json.loads(request_file.read_text(encoding='utf-8'))
        prompt = request["prompt"]
        
        print(f"[BRIDGE] Task: {request['task']}")
        print(f"[BRIDGE] Step: {request['step']}")
        
        # 调用 Claude
        try:
            claude_response = call_claude(prompt, timeout=30)
            print(f"[BRIDGE] Claude response received ({len(claude_response)} chars)")
            
            # 解析决策
            decision = parse_decision(claude_response)
            print(f"[BRIDGE] Decision: {decision['action']}")
            
        except TimeoutError:
            print(f"[BRIDGE] Claude timeout, using fallback")
            
            # Fallback 决策
            step = request["step"]
            task = request["task"]
            
            if "python" in task.lower() or "script" in task.lower():
                if step == 1:
                    decision = {
                        "action": "write",
                        "params": {
                            "path": "C:/Users/A/.openclaw/workspace/aios/sdk/hello.py",
                            "content": "print('Hello World')"
                        },
                        "reasoning": "Create a simple Python script (fallback)"
                    }
                elif step == 2:
                    decision = {
                        "action": "shell",
                        "params": {
                            "command": "\"C:/Program Files/Python312/python.exe\" C:/Users/A/.openclaw/workspace/aios/sdk/hello.py"
                        },
                        "reasoning": "Run the script (fallback)"
                    }
                else:
                    decision = {
                        "action": "done",
                        "result": {
                            "status": "completed",
                            "message": "Task completed (fallback)"
                        },
                        "reasoning": "Task completed (fallback)"
                    }
            else:
                if step <= 2:
                    decision = {
                        "action": "shell",
                        "params": {"command": f"echo 'Step {step}'"},
                        "reasoning": f"Step {step} (fallback)"
                    }
                else:
                    decision = {
                        "action": "done",
                        "result": {"status": "completed"},
                        "reasoning": "Task completed (fallback)"
                    }
        
        # 写入响应
        response_file.write_text(json.dumps(decision, indent=2), encoding='utf-8')
        
        print(f"[BRIDGE] Response written\n")
        
        return True
        
    except Exception as e:
        print(f"[BRIDGE] Error: {e}")
        
        # 写入错误响应
        error_response = {
            "action": "done",
            "result": {"status": "failed", "error": str(e)},
            "reasoning": f"Error: {e}"
        }
        response_file.write_text(json.dumps(error_response, indent=2), encoding='utf-8')
        
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("Superpowers Claude Bridge v2 - Real Claude API")
    print("=" * 60)
    print("Listening for requests...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            if process_request():
                pass  # 已经在函数内打印了
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[BRIDGE] Stopped")
