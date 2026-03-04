#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIOS API Health Check Demo - 自动修复演示
API Health Check Demo - Auto-Repair Demonstration

这个 demo 展示 AIOS 的完整闭环：
监控 API → 检测故障 → 自动修复 → 验证恢复 → 评分提升

This demo showcases AIOS's complete loop:
Monitor API → Detect failure → Auto-repair → Verify recovery → Score improvement

运行方式 / Run: python demo/api_health_demo.py
"""

import time
import threading
import http.server
import socketserver
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Dict, Any
import sys
import os
import io

# 设置 Windows 控制台 UTF-8 输出
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 彩色终端输出 / Colored terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(msg: str, color: str = Colors.ENDC):
    """带时间戳和颜色的日志"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{color}[{timestamp}] {msg}{Colors.ENDC}")

# ============================================================================
# 模拟 HTTP API 服务 / Simulated HTTP API Service
# ============================================================================

class MockAPIHandler(http.server.SimpleHTTPRequestHandler):
    """模拟 API 处理器"""
    
    def do_GET(self):
        if self.path == '/health':
            # 检查服务状态
            if getattr(self.server, 'is_healthy', True):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "ok"}')
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "error", "message": "Service degraded"}')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # 禁用默认日志
        pass

class MockAPIServer:
    """模拟 API 服务器"""
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.server: Optional[socketserver.TCPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.is_running = False
        self.is_healthy = True
    
    def start(self):
        """启动服务"""
        if self.is_running:
            return
        
        self.server = socketserver.TCPServer(("", self.port), MockAPIHandler)
        self.server.is_healthy = True
        self.is_running = True
        self.is_healthy = True
        
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        log(f"🚀 API 服务启动 (端口 {self.port})", Colors.GREEN)
    
    def stop(self):
        """停止服务"""
        if not self.is_running:
            return
        
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        self.is_running = False
        log("🛑 API 服务停止", Colors.RED)
    
    def inject_fault(self):
        """注入故障"""
        if self.server:
            self.server.is_healthy = False
            self.is_healthy = False
            log("💥 故障注入：API 返回 500", Colors.RED)
    
    def repair(self):
        """修复服务（重启）"""
        log("🔧 开始修复：重启 API 服务...", Colors.YELLOW)
        self.stop()
        time.sleep(0.5)
        self.start()
        log("✅ 修复完成：API 服务已重启", Colors.GREEN)

# ============================================================================
# 简化的 AIOS 核心组件 / Simplified AIOS Core Components
# ============================================================================

class Event:
    """事件对象"""
    def __init__(self, event_type: str, source: str, payload: Dict[str, Any]):
        self.type = event_type
        self.source = source
        self.payload = payload
        self.timestamp = int(time.time() * 1000)

class EventBus:
    """事件总线"""
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, event_type: str, handler):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    def emit(self, event: Event):
        if event.type in self.subscribers:
            for handler in self.subscribers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    log(f"❌ 订阅者错误: {e}", Colors.RED)

class Reactor:
    """自动响应引擎"""
    def __init__(self, event_bus: EventBus, api_server: MockAPIServer):
        self.event_bus = event_bus
        self.api_server = api_server
        self.event_bus.subscribe("api.health.failed", self.handle_api_failure)
    
    def handle_api_failure(self, event: Event):
        """处理 API 故障"""
        log("⚡ Reactor 触发：检测到 API 故障", Colors.YELLOW)
        log("📋 执行修复剧本：restart_api_service", Colors.CYAN)
        
        # 执行修复动作
        self.api_server.repair()
        
        # 发送修复完成事件
        self.event_bus.emit(Event(
            event_type="reactor.repair.completed",
            source="reactor",
            payload={"action": "restart_api_service"}
        ))

class HealthMonitor:
    """健康检查监控器"""
    def __init__(self, event_bus: EventBus, api_url: str, check_interval: float = 2.0):
        self.event_bus = event_bus
        self.api_url = api_url
        self.check_interval = check_interval
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.consecutive_failures = 0
        self.last_status = "unknown"
    
    def start(self):
        """启动监控"""
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        log(f"👁️  健康监控启动 (间隔 {self.check_interval}s)", Colors.CYAN)
    
    def stop(self):
        """停止监控"""
        self.is_running = False
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                # 发送健康检查请求
                req = urllib.request.Request(self.api_url, method='GET')
                with urllib.request.urlopen(req, timeout=2) as response:
                    status_code = response.getcode()
                    
                    if status_code == 200:
                        if self.last_status != "healthy":
                            log("✅ API 健康检查：正常", Colors.GREEN)
                            self.event_bus.emit(Event(
                                event_type="api.health.ok",
                                source="health_monitor",
                                payload={"status_code": status_code}
                            ))
                        self.last_status = "healthy"
                        self.consecutive_failures = 0
                    else:
                        log(f"⚠️  API 健康检查：异常 (状态码 {status_code})", Colors.YELLOW)
                        self.consecutive_failures += 1
                        if self.consecutive_failures >= 1:
                            self.event_bus.emit(Event(
                                event_type="api.health.failed",
                                source="health_monitor",
                                payload={"status_code": status_code, "failures": self.consecutive_failures}
                            ))
                        self.last_status = "unhealthy"
            
            except urllib.error.HTTPError as e:
                log(f"❌ API 健康检查：失败 (HTTP {e.code})", Colors.RED)
                self.consecutive_failures += 1
                if self.consecutive_failures >= 1:
                    self.event_bus.emit(Event(
                        event_type="api.health.failed",
                        source="health_monitor",
                        payload={"error": str(e), "failures": self.consecutive_failures}
                    ))
                self.last_status = "unhealthy"
            
            except Exception as e:
                log(f"❌ API 健康检查：失败 ({type(e).__name__})", Colors.RED)
                self.consecutive_failures += 1
                if self.consecutive_failures >= 1:
                    self.event_bus.emit(Event(
                        event_type="api.health.failed",
                        source="health_monitor",
                        payload={"error": str(e), "failures": self.consecutive_failures}
                    ))
                self.last_status = "unhealthy"
            
            time.sleep(self.check_interval)

class ScoreTracker:
    """评分追踪器"""
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.score = 100.0
        self.event_bus.subscribe("api.health.failed", self.on_failure)
        self.event_bus.subscribe("api.health.ok", self.on_recovery)
    
    def on_failure(self, event: Event):
        """故障时降分"""
        self.score = max(0, self.score - 10)
        log(f"📉 系统评分下降: {self.score:.1f}/100", Colors.RED)
    
    def on_recovery(self, event: Event):
        """恢复时加分"""
        if self.score < 100:
            self.score = min(100, self.score + 15)
            log(f"📈 系统评分恢复: {self.score:.1f}/100", Colors.GREEN)

# ============================================================================
# Demo 主流程 / Main Demo Flow
# ============================================================================

def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}AIOS API Health Check Demo - 自动修复演示{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")
    
    log("🎬 Demo 开始", Colors.BOLD)
    
    # 初始化组件
    event_bus = EventBus()
    api_server = MockAPIServer(port=8765)
    reactor = Reactor(event_bus, api_server)
    monitor = HealthMonitor(event_bus, "http://localhost:8765/health", check_interval=2.0)
    score_tracker = ScoreTracker(event_bus)
    
    try:
        # 1. 启动 API 服务
        log("\n📍 阶段 1: 启动 API 服务", Colors.BOLD)
        api_server.start()
        time.sleep(1)
        
        # 2. 启动健康监控
        log("\n📍 阶段 2: 启动健康监控", Colors.BOLD)
        monitor.start()
        time.sleep(3)
        
        # 3. 正常运行一段时间
        log("\n📍 阶段 3: 正常运行中...", Colors.BOLD)
        log("⏱️  等待 6 秒（观察正常状态）", Colors.CYAN)
        time.sleep(6)
        
        # 4. 注入故障
        log("\n📍 阶段 4: 模拟故障", Colors.BOLD)
        api_server.inject_fault()
        
        # 5. 等待检测和自动修复
        log("\n📍 阶段 5: 等待 AIOS 自动修复...", Colors.BOLD)
        log("⏱️  等待 5 秒（观察故障检测和修复）", Colors.CYAN)
        time.sleep(5)
        
        # 6. 验证恢复
        log("\n📍 阶段 6: 验证修复结果", Colors.BOLD)
        log("⏱️  等待 4 秒（观察恢复状态）", Colors.CYAN)
        time.sleep(4)
        
        # 7. 总结
        log("\n" + "="*70, Colors.BOLD)
        log("🎉 Demo 完成！", Colors.BOLD + Colors.GREEN)
        log(f"📊 最终系统评分: {score_tracker.score:.1f}/100", Colors.BOLD)
        log("\n✨ AIOS 完整闭环演示：", Colors.BOLD)
        log("   1. ✅ 监控 API 健康状态", Colors.GREEN)
        log("   2. ✅ 检测到故障（HTTP 500）", Colors.GREEN)
        log("   3. ✅ EventBus 发送故障事件", Colors.GREEN)
        log("   4. ✅ Reactor 自动触发修复", Colors.GREEN)
        log("   5. ✅ 重启服务恢复正常", Colors.GREEN)
        log("   6. ✅ 系统评分自动恢复", Colors.GREEN)
        log("="*70 + "\n", Colors.BOLD)
        
    except KeyboardInterrupt:
        log("\n⚠️  用户中断", Colors.YELLOW)
    finally:
        # 清理
        monitor.stop()
        api_server.stop()
        log("🧹 清理完成", Colors.CYAN)

if __name__ == "__main__":
    # Windows 控制台颜色支持
    if sys.platform == "win32":
        os.system("chcp 65001 >nul 2>&1")
    
    main()
