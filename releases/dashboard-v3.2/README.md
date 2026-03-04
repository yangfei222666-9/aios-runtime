# AIOS Dashboard v3.2

🚀 **自我进化操作系统 · 实时控制中心**

实时监控 AIOS 系统状态，展示 Agent 性能、Evolution Score、事件流等核心指标。

## ✨ 功能特性

### 核心指标
- **活跃 Agent 数量** - 实时统计
- **Evolution Score** - 系统进化评分
- **今日改进次数** - 自动优化统计
- **成功率** - 任务执行成功率

### 实时趋势
- 成功率曲线（最近20个数据点）
- Evolution Score 走势
- 渐变填充 + 数据点可视化

### Agent 状态
- 4个 Agent 实时监控
- 成功率 + 任务数
- 运行状态（运行中/空闲）
- 渐变进度条

### 事件流
- 最近10条真实事件
- 事件类型图标（✅⚡🔮🔄）
- 真实时间戳
- 颜色分类（成功/警告/错误/进化）

## 🚀 快速开始

### 环境要求
- Python 3.8+
- AIOS 系统（需要 `events.jsonl` 和 `agents_data.json`）

### 安装步骤

1. **解压文件**
   ```bash
   unzip AIOS-Dashboard-v3.2.zip
   cd dashboard-v3.2
   ```

2. **启动服务器**
   
   **Windows（后台运行）：**
   ```cmd
   start_dashboard_silent.bat
   ```
   
   **手动启动：**
   ```bash
   python server.py
   ```

3. **访问 Dashboard**
   ```
   http://127.0.0.1:9091
   ```

## 📊 数据源

Dashboard 从以下文件读取真实数据：

- `../events.jsonl` - AIOS 事件日志
- `../agent_system/agents_data.json` - Agent 配置和统计

确保这些文件存在且路径正确。

## ⚙️ 配置

### 修改端口
编辑 `server.py`，修改最后一行：
```python
start_server(9091)  # 改成你想要的端口
```

### 修改刷新频率
编辑 `server.py`，找到：
```python
time.sleep(5.0)  # 每 5 秒推送一次
```

## 🛠️ 技术栈

- **前端：** Tailwind CSS + Chart.js + Font Awesome
- **后端：** Python 3 标准库（无额外依赖）
- **通信：** Server-Sent Events (SSE)

## 📝 版本历史

### v3.2 (2026-02-25)
- ✅ Agent 卡片优化（状态标签、渐变进度条）
- ✅ 真实事件流（从 events.jsonl 读取）
- ✅ 后台运行模式（无窗口）
- ✅ 图表高度优化（120px）

### v3.1 (2026-02-25)
- ✅ CountUp 数字动画
- ✅ 趋势数组推送
- ✅ 真实时间戳显示

### v3.0 (2026-02-25)
- ✅ 初始版本
- ✅ SSE 实时推送
- ✅ 真实数据源接入

## 🐛 故障排除

### 端口被占用
```bash
# Windows
netstat -ano | findstr :9091
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :9091
kill -9 <PID>
```

### 数据不更新
1. 检查 `events.jsonl` 是否存在
2. 检查文件路径是否正确
3. 查看浏览器控制台是否有错误

### SSE 连接失败
- 刷新浏览器
- 检查服务器是否运行
- 查看防火墙设置

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Made with ❤️ for AIOS**
