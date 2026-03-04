# AIOS Dashboard - SSE 实时推送版本

## 功能特性

✅ **零外部依赖** - 只用 Python 标准库  
✅ **SSE 实时推送** - 每秒自动更新数据  
✅ **断线自动重连** - 5 秒后自动重试  
✅ **优雅降级** - SSE 不可用时自动切换到轮询模式  
✅ **连接状态指示** - 绿点=已连接，红点=断开  
✅ **实时事件流** - 显示最近 10 条事件  
✅ **系统监控** - CPU、内存使用率实时显示  
✅ **Windows 兼容** - 完全支持 Windows 环境  

## 快速启动

### 方式 1：双击启动（推荐）
```
双击 start_sse_dashboard.bat
```

### 方式 2：命令行启动
```bash
cd C:\Users\A\.openclaw\workspace\aios\dashboard
python sse_server.py
```

### 方式 3：自定义端口
```bash
python sse_server.py 9000
```

## 访问地址

- **Dashboard 主页**: http://localhost:8080
- **SSE 推送流**: http://localhost:8080/api/metrics/stream
- **Metrics API**: http://localhost:8080/api/metrics
- **Events API**: http://localhost:8080/api/events

## 技术实现

### 后端 (sse_server.py)
- 基于 `http.server.HTTPServer` 和 `SimpleHTTPRequestHandler`
- SSE (Server-Sent Events) 协议实现
- 每秒推送一次 metrics snapshot
- 支持 CORS 跨域访问
- 自动处理客户端断开连接

### 前端 (index.html)
- 使用原生 `EventSource` API 连接 SSE
- 自动断线重连机制（5 秒间隔）
- 降级到轮询模式（2 秒间隔）
- 实时更新 UI（无需手动刷新）
- 连接状态可视化指示器

## 数据推送内容

每秒推送的数据包括：

```json
{
  "counters": {
    "tasks.total": 100,
    "tasks.success": 95,
    "tasks.failed": 5
  },
  "gauges": {
    "queue.size": 10,
    "active.workers": 4
  },
  "system": {
    "cpu_percent": 25.5,
    "memory_percent": 60.2,
    "timestamp": 1234567890.123
  },
  "histograms": [],
  "timestamp": 1234567890.123
}
```

## 优势对比

| 特性 | SSE 方案 | WebSocket 方案 |
|------|----------|----------------|
| 实现复杂度 | ⭐ 简单 | ⭐⭐⭐ 复杂 |
| 标准库支持 | ✅ 完全支持 | ❌ 需要第三方库 |
| 浏览器兼容 | ✅ 原生支持 | ✅ 原生支持 |
| 自动重连 | ✅ 浏览器自动 | ❌ 需要手动实现 |
| 单向推送 | ✅ 完美适配 | ⚠️ 功能过剩 |
| 资源占用 | ⭐ 低 | ⭐⭐ 中等 |

## 故障排查

### 问题：连接一直显示"断开"
**解决方案**：
1. 检查服务器是否正常启动
2. 确认端口 8080 没有被占用
3. 查看浏览器控制台错误信息

### 问题：数据不更新
**解决方案**：
1. 刷新页面重新连接
2. 检查 AIOS metrics 模块是否正常
3. 查看服务器日志输出

### 问题：CPU/内存数据不显示
**解决方案**：
- 安装 psutil 库（可选）：`pip install psutil`
- 不安装也能正常运行，只是缺少系统监控数据

## 停止服务器

在服务器窗口按 `Ctrl+C` 即可停止。

## 与旧版本对比

| 版本 | 更新方式 | 依赖 | 实时性 |
|------|----------|------|--------|
| dashboard_server.py | 手动刷新 | 无 | ❌ |
| sse_server.py | 自动推送 | 无 | ✅ 每秒 |

## 下一步优化

- [ ] 添加历史数据图表（Chart.js）
- [ ] 支持多客户端广播
- [ ] 添加告警阈值配置
- [ ] 导出数据为 CSV/JSON
- [ ] 移动端响应式优化

---

**作者**: AIOS Team  
**更新时间**: 2024  
**许可**: MIT
