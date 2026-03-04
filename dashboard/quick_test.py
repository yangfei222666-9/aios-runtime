"""最简化 SSE 测试服务器 - 端口 8888"""
import json
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = 8888

class SimpleSSEHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/metrics':
            # 返回 JSON 数据（轮询接口）
            import random
            data = {
                'active_agents': 5,
                'evolution_score': round(0.40 + random.random() * 0.10, 2),
                'today_improvements': random.randint(2, 5),
                'success_rate': random.randint(80, 95),
                'resources': {
                    'cpu': random.randint(20, 40),
                    'mem': random.randint(50, 70),
                    'disk': random.randint(40, 50),
                    'gpu': random.randint(25, 35)
                },
                'agents': [
                    {'name': 'Coder', 'pid': 12345, 'alive': True, 'status': 'active', 'success_rate': random.randint(85, 95), 'last_active': time.time()},
                    {'name': 'Analyst', 'pid': 12346, 'alive': True, 'status': 'active', 'success_rate': random.randint(80, 90), 'last_active': time.time()},
                ],
                'top_errors': [
                    {'error': 'Connection timeout', 'count': random.randint(3, 8)},
                    {'error': 'File not found', 'count': random.randint(2, 5)},
                ],
                'slow_ops': [
                    {'operation': 'Database query', 'duration': random.randint(1000, 2000)},
                    {'operation': 'API call', 'duration': random.randint(800, 1500)},
                ],
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            
        elif self.path == '/api/metrics/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                counter = 0
                while True:
                    data = {
                        'active_agents': 5,
                        'evolution_score': 0.45,
                        'today_improvements': 3,
                        'success_rate': 85,
                        'resources': {
                            'cpu': 25,
                            'mem': 60,
                            'disk': 45,
                            'gpu': 30
                        },
                        'agents': [
                            {'name': 'Coder', 'pid': 12345, 'alive': True, 'status': 'active', 'success_rate': 90, 'last_active': time.time()},
                            {'name': 'Analyst', 'pid': 12346, 'alive': True, 'status': 'active', 'success_rate': 85, 'last_active': time.time()},
                        ],
                        'top_errors': [
                            {'error': 'Connection timeout', 'count': 5},
                        ],
                        'slow_ops': [
                            {'operation': 'Database query', 'duration': 1500},
                        ],
                        'counter': counter
                    }
                    
                    message = f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                    self.wfile.write(message.encode('utf-8'))
                    self.wfile.flush()
                    
                    counter += 1
                    time.sleep(3)
                    
            except (BrokenPipeError, ConnectionResetError):
                pass
        
        elif self.path == '/' or self.path == '/index.html':
            dashboard_file = Path(__file__).parent / "index.html"
            if dashboard_file.exists():
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                with open(dashboard_file, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
        else:
            self.send_error(404)
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path == '/api/control/evolve':
            # 手动触发进化
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            result = {
                "success": True,
                "new_score": 0.52,
                "improvements": "优化了 3 个 Agent 配置"
            }
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            
        elif self.path == '/api/control/agent':
            # 启动/停止 Agent
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
            
            agent_name = data.get('name', '')
            action = data.get('action', '')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            result = {
                "success": True,
                "status": f"Agent {agent_name} 已{action == 'start' and '启动' or '停止'}"
            }
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        else:
            # 未知接口
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            result = {"success": False, "message": "未知接口"}
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        if '/api/metrics/stream' not in format:
            print(f"[{self.address_string()}] {format % args}")

print("=" * 60)
print(f"Dashboard 启动: http://localhost:{PORT}")
print(f"SSE: http://localhost:{PORT}/api/metrics/stream")
print("=" * 60)

httpd = HTTPServer(('127.0.0.1', PORT), SimpleSSEHandler)
httpd.serve_forever()
