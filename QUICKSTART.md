# AIOS v1.0 快速开始指南

## 📋 系统要求

- **Python 3.8+**（推荐 3.10+）
- **操作系统**：Windows / Linux / macOS
- **磁盘空间**：至少 10 MB
- **零依赖**：无需安装任何第三方库

---

## 🚀 5分钟快速开始

### 1️⃣ 解压文件

```bash
# Windows
右键 AIOS-v1.0-demo.zip → 解压到当前文件夹

# Linux/Mac
unzip AIOS-v1.0-demo.zip
```

### 2️⃣ 进入目录

```bash
cd aios
```

### 3️⃣ 运行演示

```bash
python aios.py demo
```

**预期输出：**
```
✅ AIOS v1.0 演示
📊 系统状态：健康
🔧 核心组件：EventBus, Scheduler, Reactor
```

---

## 🎯 核心功能

### 查看系统状态

```bash
python aios.py status
```

**输出示例：**
```
Evolution Score: 0.45 (healthy)
Reactor执行率: 52.5%
事件总数: 1234
Agent数量: 5
```

### 启动监控面板

```bash
python aios.py dashboard
```

**访问地址：** http://localhost:8080

**功能：**
- 实时系统状态
- Agent 性能监控
- 事件日志查看
- 进化历史追踪

### 查看版本信息

```bash
python aios.py version
```

---

## 🛠️ 常见问题

### Q1: 提示 "python 不是内部或外部命令"

**Windows 解决方案：**
```bash
# 方法1：使用完整路径
C:\Python312\python.exe aios.py demo

# 方法2：添加到环境变量
# 控制面板 → 系统 → 高级系统设置 → 环境变量 → Path → 添加 Python 安装路径
```

**Linux/Mac 解决方案：**
```bash
# 使用 python3
python3 aios.py demo
```

### Q2: 提示 "找不到模块"

**检查 Python 版本：**
```bash
python --version
# 必须是 3.8 或更高
```

**如果版本过低：**
- Windows: 从 [python.org](https://www.python.org/downloads/) 下载最新版
- Linux: `sudo apt install python3.10`
- Mac: `brew install python@3.10`

### Q3: Dashboard 打不开

**检查端口占用：**
```bash
# Windows
netstat -ano | findstr :8080

# Linux/Mac
lsof -i :8080
```

**更换端口：**
```bash
python aios.py dashboard --port 8888
```

### Q4: 权限问题

**AIOS 不需要管理员权限！**

如果遇到权限错误：
- 检查文件夹是否只读
- 确保当前用户有写入权限
- 避免安装在系统目录（如 C:\Program Files）

---

## 📚 进阶使用

### 自定义配置

编辑 `config.yaml`：

```yaml
# 修改 Dashboard 端口
dashboard:
  port: 8080
  host: "0.0.0.0"

# 调整 Scheduler 频率
scheduler:
  interval: 60  # 秒

# 配置通知
notifications:
  telegram:
    enabled: false
```

### 查看日志

```bash
# 实时日志
tail -f aios/core/data/events.jsonl

# Windows
Get-Content aios/core/data/events.jsonl -Wait
```

### 清理数据

```bash
# 清理 7 天前的事件
python aios.py cleanup --days 7

# 完全重置（谨慎！）
python aios.py reset
```

---

## 🎓 学习资源

### 核心概念

1. **EventBus** - 事件总线，系统心脏
2. **Scheduler** - 决策调度，系统大脑
3. **Reactor** - 自动修复，免疫系统
4. **Agent** - 执行单元，工作者

### 工作流程

```
错误发生 → EventBus → Scheduler → Reactor → 自动修复 → 验证 → 评分上升
```

### 文档位置

- **完整文档**: `README.md`
- **API 参考**: `API.md`
- **架构设计**: `ARCHITECTURE.md`

---

## 💡 使用建议

### 第一次使用

1. 先运行 `python aios.py demo` 确认环境正常
2. 再运行 `python aios.py status` 查看系统状态
3. 最后启动 `python aios.py dashboard` 体验可视化界面

### 日常使用

- **监控模式**: 保持 Dashboard 开启，实时查看系统状态
- **定期检查**: 每天运行 `python aios.py status` 查看健康度
- **数据清理**: 每周运行 `python aios.py cleanup` 清理旧数据

### 性能优化

- **降低心跳频率**: 修改 `config.yaml` 中的 `scheduler.interval`
- **限制日志大小**: 定期运行 `cleanup` 命令
- **关闭不需要的 Agent**: 编辑 `agent_system/agents.yaml`

---

## 🆘 获取帮助

### 命令行帮助

```bash
python aios.py --help
python aios.py demo --help
python aios.py status --help
```

### 联系方式

- **GitHub**: [你的 GitHub 仓库]
- **Email**: [你的邮箱]
- **Telegram**: @shh7799

---

## 📝 下一步

1. ✅ 完成快速开始
2. 📖 阅读 `README.md` 了解完整功能
3. 🎯 尝试自定义配置
4. 🚀 集成到你的项目中

**祝你使用愉快！** 🎉
