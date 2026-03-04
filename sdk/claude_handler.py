"""
Claude Request Handler - 在 OpenClaw 主会话中运行

这个脚本监听 claude_request.flag
当发现请求时，读取 prompt 并通过 Telegram 发送给我（Claude）
我会回复决策，然后写入 claude_response.json
"""

import json
import time
from pathlib import Path


def check_claude_request():
    """检查是否有 Claude 请求"""
    comm_dir = Path("C:/Users/A/.openclaw/workspace/aios/sdk/.comm")
    claude_request = comm_dir / "claude_request.json"
    claude_response = comm_dir / "claude_response.json"
    claude_flag = comm_dir / "claude_request.flag"
    
    if not claude_flag.exists():
        return False
    
    try:
        # 读取请求
        request = json.loads(claude_request.read_text(encoding='utf-8'))
        prompt = request["prompt"]
        
        print(f"\n[HANDLER] Found Claude request")
        print(f"[HANDLER] Prompt length: {len(prompt)} chars")
        print(f"[HANDLER] Prompt preview: {prompt[:200]}...")
        
        # 这里应该通过 sessions_send 或其他方式调用 Claude
        # 但现在我们在 OpenClaw 主会话中，可以直接返回
        
        # 示例响应（实际应该是 Claude 的真实响应）
        response_text = """Based on the task, here's my decision:

{
  "action": "write",
  "params": {
    "path": "C:/Users/A/.openclaw/workspace/aios/sdk/hello.py",
    "content": "print('Hello World from Claude!')"
  },
  "reasoning": "Create a Python script as requested"
}"""
        
        # 写入响应
        response = {
            "response": response_text,
            "timestamp": time.time()
        }
        claude_response.write_text(json.dumps(response, indent=2), encoding='utf-8')
        
        print(f"[HANDLER] Response written")
        
        return True
        
    except Exception as e:
        print(f"[HANDLER] Error: {e}")
        return False


if __name__ == "__main__":
    print("Claude Request Handler - Listening...")
    print("This script should run in OpenClaw main session")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            if check_claude_request():
                print("[HANDLER] Request processed\n")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[HANDLER] Stopped")
