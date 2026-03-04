"""
AIOS Dashboard SSE Server - Server-Sent Events 实时推送
零外部依赖，只用 Python 标准库
"""
import json
import time
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

AIOS_ROOT = Path(__file__).parent.parent


class SSEHandler(SimpleHTTPRequestHandler):
    """SSE 处理器 - 支持实时推送"""
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        
        # SSE 实时流
        if parsed_path.path == '/api/metrics/stream':
            self.serve_sse_stream()
        # 普通 API
        elif parsed_path.path == '/api/metrics':
            self.serve_metrics()
        elif parsed_path.path == '/api/events':
            self.serve_events()
        # 静态文件
        elif parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_dashboard()
        else:
            self.send_error(404, "File not found")
    
    def serve_sse_stream(self):
        """SSE 实时推送流"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            while True:
                # 获取实时数据
                data = self.get_realtime_metrics()
                
                # 发送 SSE 格式数据
                message = f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                self.wfile.write(message.encode('utf-8'))
                self.wfile.flush()
                
                # 每 3 秒推送一次（降低频率）
                time.sleep(3)
                
        except (BrokenPipeError, ConnectionResetError):
            # 客户端断开连接
            pass
        except Exception as e:
            print(f"SSE stream error: {e}")
    
    def get_realtime_metrics(self):
        """获取实时指标数据"""
        try:
            # 尝试导入 AIOS metrics
            from aios.observability.metrics import METRICS
            snapshot = METRICS.snapshot()
            
            # 添加系统信息（非阻塞采样）
            import psutil
            snapshot['system'] = {
                'cpu_percent': psutil.cpu_percent(interval=None),  # 非阻塞
                'memory_percent': psutil.virtual_memory().percent,
                'timestamp': time.time()
            }
            
            return snapshot
            
        except ImportError:
            # 如果没有 psutil，返回基础数据
            try:
                from aios.observability.metrics import METRICS
                return METRICS.snapshot()
            except:
                # 返回模拟数据
                return {
                    'counters': {
                        'tasks.total': 0,
                        'tasks.success': 0,
                        'tasks.failed': 0
                    },
                    'gauges': {},
                    'histograms': [],
                    'timestamp': time.time()
                }
    
    def serve_dashboard(self):
        """提供 Dashboard HTML"""
        dashboard_file = AIOS_ROOT / "dashboard" / "index.html"
        
        if not dashboard_file.exists():
            self.send_error(404, "Dashboard not found")
            return
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        with open(dashboard_file, 'rb') as f:
            self.wfile.write(f.read())
    
    def serve_metrics(self):
        """提供 Metrics 快照（非流式）"""
        data = self.get_realtime_metrics()
        self.send_json(data)
    
    def serve_events(self):
        """提供最近事件"""
        events_file = AIOS_ROOT.parent / "events.jsonl"
        events = []
        
        if events_file.exists():
            try:
                with open(events_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line in lines[-10:]:  # 最近 10 条
                    if line.strip():
                        try:
                            event = json.loads(line)
                            events.append(event)
                        except:
                            pass
            except Exception as e:
                print(f"Error reading events: {e}")
        
        events.reverse()  # 最新的在前
        self.send_json(events)
    
    def send_json(self, data):
        """发送 JSON 响应"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(json_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        # 过滤掉 SSE 的频繁日志
        if '/api/metrics/stream' not in format:
            print(f"[Dashboard] {self.address_string()} - {format % args}")


def start_sse_server(port=8080):
    """启动 SSE 服务器"""
    import sys
    import io
    
    # 修复 Windows 控制台编码问题
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, SSEHandler)
    
    print("=" * 60)
    print("🚀 AIOS Dashboard SSE Server 启动成功!")
    print("=" * 60)
    print(f"📊 Dashboard 地址: http://localhost:{port}")
    print(f"🔄 SSE 推送地址: http://localhost:{port}/api/metrics/stream")
    print(f"📡 实时更新频率: 每 3 秒 1 次")
    print(f"⏹️  按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard 服务器已停止")
        httpd.shutdown()


if __name__ == "__main__":
    import sys
    
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            print("Usage: python sse_server.py [port]")
            sys.exit(1)
    
    start_sse_server(port)
