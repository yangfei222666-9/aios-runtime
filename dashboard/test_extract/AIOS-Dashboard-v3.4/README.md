# AIOS Dashboard v3.4

## 快速开始

### Windows
```cmd
python server.py
```

### Linux/Mac
```bash
python3 server.py
```

然后打开浏览器访问：http://localhost:8888

## 功能特性

- ✅ 实时监控 AIOS 系统状态
- ✅ Agent 状态管理
- ✅ Evolution Score 趋势
- ✅ 错误统计和慢操作分析
- ✅ 系统资源监控
- ✅ 手动触发进化
- ✅ Agent 启动/停止控制

## 数据来源

Dashboard 会自动读取以下数据：
1. `../agent_system/data/agents/*.json` - Agent 状态
2. `../../events.jsonl` - 事件日志
3. `../learning/metrics_history.jsonl` - 历史指标

如果没有真实数据，会显示演示数据。

## 系统要求

- Python 3.8+
- psutil（可选，用于系统资源监控）

安装依赖：
```bash
pip install psutil
```

## 端口配置

默认端口：8888

修改端口：编辑 `server.py`，修改 `PORT = 8888`

## 技术栈

- 前端：HTML + Tailwind CSS + Chart.js
- 后端：Python http.server
- 数据更新：轮询模式（每 3 秒）

## 版本信息

- 版本：v3.4
- 发布日期：2026-02-26
- 作者：AIOS Team

## 许可证

MIT License
