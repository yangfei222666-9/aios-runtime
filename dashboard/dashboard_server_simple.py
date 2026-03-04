"""
AIOS Dashboard Server - 简化版（确保稳定）
"""
import json
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime
import psutil

AIOS_ROOT = Path(__file__).parent.parent


class DashboardHandler(BaseHTTPRequestHandler):
    """Dashboard HTTP 处理器"""
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/agents':
            self.serve_agents()
        elif parsed_path.path == '/api/status':
            self.serve_status()
        elif parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_dashboard()
        else:
            self.send_error(404, "File not found")
    
    def do_POST(self):
        """处理 POST 请求"""
        if self.path.startswith('/api/control/agent/'):
            parts = self.path.split('/')
            if len(parts) < 6:
                self.send_error(400, "Invalid request")
                return
            
            agent_name = parts[4]
            action = parts[5]
            
            response = self.handle_agent_control(agent_name, action)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404, "API not found")
    
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
    
    def serve_agents(self):
        """提供 Agent 列表"""
        import sys
        sys.path.insert(0, str(AIOS_ROOT))
        
        try:
            from agent_system.process_manager import AgentProcessManager
            manager = AgentProcessManager()
            agent_status = manager.get_all_status()
            
            agents = []
            for name, status in agent_status.items():
                agents.append({
                    'id': name,
                    'name': name,
                    'status': 'active' if status.get('alive') else 'archived',
                    'model': 'claude-sonnet-4-6'
                })
            
            self.send_json({'agents': agents})
        except Exception as e:
            print(f"读取 Agent 列表失败: {e}")
            self.send_json({'agents': []})
    
    def serve_status(self):
        """提供系统状态（简化版，单次返回）"""
        import sys
        sys.path.insert(0, str(AIOS_ROOT))
        
        try:
            from agent_system.process_manager import AgentProcessManager
            manager = AgentProcessManager()
            agent_status = manager.get_all_status()
            
            active_agents = sum(1 for a in agent_status.values() if a.get('alive', False))
            
            data = {
                "active_agents": active_agents,
                "evolution_score": 0,
                "improvements_today": 0,
                "success_rate": 0,
                "cpu": int(psutil.cpu_percent(interval=0.1)),
                "mem": int(psutil.virtual_memory().percent),
                "disk": int(psutil.disk_usage('/').percent),
                "gpu": None,
                "agents": []
            }
            
            for name, status in agent_status.items():
                data["agents"].append({
                    "name": name,
                    "status": "running" if status.get('alive') else "stopped",
                    "pid": status.get('pid')
                })
            
            self.send_json(data)
        except Exception as e:
            print(f"读取状态失败: {e}")
            self.send_json({"error": str(e)})
    
    def handle_agent_control(self, agent_name, action):
        """Agent 启停控制"""
        try:
            import sys
            sys.path.insert(0, str(AIOS_ROOT))
            from agent_system.orchestrator import AgentOrchestrator
            
            orchestrator = AgentOrchestrator()
            
            if action == "start":
                result = orchestrator.start_agent(agent_name)
            else:
                result = orchestrator.stop_agent(agent_name)
            
            print(f"Agent {agent_name}: {action} -> {result}")
            
            if result.get('success'):
                return {
                    "status": "success",
                    "agent": agent_name,
                    "action": action,
                    "new_status": "running" if action == "start" else "stopped",
                    "pid": result.get('pid')
                }
            else:
                return {
                    "status": "error",
                    "agent": agent_name,
                    "message": result.get('error')
                }
        except Exception as e:
            print(f"Agent 控制失败: {e}")
            return {"status": "error", "message": str(e)}
    
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
        print(f"[Dashboard] {format % args}")


def start_dashboard(port=9091):
    """启动 Dashboard 服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    
    print(f"AIOS Dashboard 启动成功!")
    print(f"访问地址: http://localhost:{port}")
    print(f"按 Ctrl+C 停止服务器")
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard 服务器已停止")
        httpd.shutdown()


if __name__ == "__main__":
    import sys
    
    port = 9091
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            print("Usage: python dashboard_server_simple.py [port]")
            sys.exit(1)
    
    start_dashboard(port)
