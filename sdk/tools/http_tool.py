"""
HTTP Tool for Superpowers Mode

支持 GET/POST/PUT/DELETE 等 HTTP 请求
"""

import json
import subprocess
from typing import Dict, Any, Optional


def http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    执行 HTTP 请求
    
    Args:
        method: HTTP 方法（GET/POST/PUT/DELETE）
        url: 请求 URL
        headers: 请求头
        data: 请求数据（POST/PUT）
        timeout: 超时时间（秒）
        
    Returns:
        响应结果
    """
    try:
        # 使用 curl 执行请求
        cmd = ["curl", "-X", method, url, "-s", "-w", "\\n%{http_code}"]
        
        # 添加请求头
        if headers:
            for key, value in headers.items():
                cmd.extend(["-H", f"{key}: {value}"])
        
        # 添加请求数据
        if data:
            cmd.extend(["-H", "Content-Type: application/json"])
            cmd.extend(["-d", json.dumps(data)])
        
        # 执行请求
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr or "Request failed"
            }
        
        # 解析响应
        output = result.stdout.strip()
        lines = output.split('\n')
        
        if len(lines) < 2:
            return {
                "success": False,
                "error": "Invalid response format"
            }
        
        status_code = int(lines[-1])
        body = '\n'.join(lines[:-1])
        
        # 尝试解析 JSON
        try:
            body_json = json.loads(body)
        except:
            body_json = None
        
        return {
            "success": 200 <= status_code < 300,
            "status_code": status_code,
            "body": body,
            "body_json": body_json
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Request timeout ({timeout}s)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# 便捷函数
def get(url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
    """GET 请求"""
    return http_request("GET", url, headers=headers, **kwargs)


def post(url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
    """POST 请求"""
    return http_request("POST", url, headers=headers, data=data, **kwargs)


def put(url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
    """PUT 请求"""
    return http_request("PUT", url, headers=headers, data=data, **kwargs)


def delete(url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
    """DELETE 请求"""
    return http_request("DELETE", url, headers=headers, **kwargs)


if __name__ == "__main__":
    # 测试
    print("Testing HTTP tool...")
    
    # 测试 GET
    result = get("https://api.github.com/repos/openclaw/openclaw")
    print(f"\nGET test:")
    print(f"  Success: {result['success']}")
    print(f"  Status: {result.get('status_code')}")
    if result.get('body_json'):
        print(f"  Name: {result['body_json'].get('name')}")
        print(f"  Stars: {result['body_json'].get('stargazers_count')}")
    
    # 测试 POST（示例）
    # result = post("https://httpbin.org/post", data={"test": "data"})
    # print(f"\nPOST test:")
    # print(f"  Success: {result['success']}")
    # print(f"  Status: {result.get('status_code')}")
