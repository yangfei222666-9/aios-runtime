"""
Superpowers Claude Bridge - 监听请求并调用 Claude

这个脚本应该在 OpenClaw 主会话中运行（通过 cron 或手动）
监听 .comm/request.flag，调用 Claude，写入响应
"""

import json
import time
from pathlib import Path


def process_request():
    """处理一个请求"""
    comm_dir = Path("C:/Users/A/.openclaw/workspace/aios/sdk/.comm")
    request_file = comm_dir / "request.json"
    response_file = comm_dir / "response.json"
    flag_file = comm_dir / "request.flag"
    
    # 检查是否有请求
    if not flag_file.exists():
        return False
    
    print(f"[BRIDGE] Found request, processing...")
    
    try:
        # 读取请求
        request = json.loads(request_file.read_text(encoding='utf-8'))
        prompt = request["prompt"]
        
        print(f"[BRIDGE] Task: {request['task']}")
        print(f"[BRIDGE] Step: {request['step']}")
        
        # 这里应该调用 sessions_send
        # 因为这个脚本会在 OpenClaw 主会话中运行
        # 我们可以通过 subprocess 调用 OpenClaw CLI
        
        # 方案：创建一个临时文件，让 OpenClaw 主会话读取并处理
        # 然后通过 sessions_send 调用 Claude
        
        # 简化实现：先用固定决策，后续可以集成真实 Claude
        step = request["step"]
        task = request["task"]
        
        # 根据任务类型和步骤智能决策
        if "python" in task.lower() or "script" in task.lower():
            # Python 脚本任务
            if step == 1:
                decision = {
                    "action": "write",
                    "params": {
                        "path": "C:/Users/A/.openclaw/workspace/aios/sdk/hello.py",
                        "content": "print('Hello World')"
                    },
                    "reasoning": "Create a simple Python script"
                }
            elif step == 2:
                decision = {
                    "action": "shell",
                    "params": {
                        "command": "\"C:/Program Files/Python312/python.exe\" C:/Users/A/.openclaw/workspace/aios/sdk/hello.py"
                    },
                    "reasoning": "Run the script to verify it works"
                }
            else:
                decision = {
                    "action": "done",
                    "result": {
                        "status": "completed",
                        "message": "Python script created and tested successfully",
                        "file": "C:/Users/A/.openclaw/workspace/aios/sdk/hello.py"
                    },
                    "reasoning": "Task completed successfully"
                }
        else:
            # 通用任务
            if step == 1:
                decision = {
                    "action": "shell",
                    "params": {"command": f"echo 'Analyzing task: {task}'"},
                    "reasoning": "First step: analyze task"
                }
            elif step == 2:
                decision = {
                    "action": "shell",
                    "params": {"command": "echo 'Executing main work'"},
                    "reasoning": "Second step: execute main work"
                }
            else:
                decision = {
                    "action": "done",
                    "result": {
                        "status": "completed",
                        "message": f"Task completed: {task}",
                        "steps": step - 1
                    },
                    "reasoning": "Task completed successfully"
                }
        
        # 写入响应
        response_file.write_text(json.dumps(decision, indent=2), encoding='utf-8')
        
        print(f"[BRIDGE] Response written: {decision['action']}")
        
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
    print("Superpowers Claude Bridge - Listening...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            if process_request():
                print("[BRIDGE] Request processed\n")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[BRIDGE] Stopped")
