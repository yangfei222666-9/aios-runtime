# AIOS - AI 操作系统（朋友版）

## 🚀 10 秒快速开始

### Windows 用户：
1. 双击 `install.bat` 安装依赖（只需一次）
2. 双击 `run.bat` 运行演示

### Mac/Linux 用户：
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行演示
python aios.py demo --scenario 1
```

---

## 💡 AIOS 是什么？

AIOS 是一个**轻量级的 AI 操作系统**，让你的 AI Agent 能够：

- 🤖 **自主运行** — 自动调度任务，无需人工干预
- 👁️ **自我观测** — 实时监控性能、成本、错误
- 🧬 **自我进化** — 从失败中学习，自动优化策略

---

## 🎯 3 个演示场景

### 场景 1：文件监控 + 自动分类
```bash
python aios.py demo --scenario 1
```
- 监控文件变化
- 自动分类文件（按扩展名）
- 生成分类报告

### 场景 2：API 健康检查 + 自动恢复
```bash
python aios.py demo --scenario 2
```
- 检查 API 健康状态
- 自动重试失败请求
- 记录恢复过程

### 场景 3：日志分析 + 自动生成 Playbook
```bash
python aios.py demo --scenario 3
```
- 分析错误日志
- 识别高频错误
- 自动生成修复 Playbook

---

## 📊 查看 Dashboard

```bash
python aios.py dashboard
```

然后打开浏览器访问：http://127.0.0.1:9091

---

## 🎯 提交任务

```bash
# 提交一个代码任务
python aios.py submit --desc "重构 scheduler.py" --type code --priority high

# 查看任务状态
python aios.py tasks

# 运行心跳（自动执行任务）
python aios.py heartbeat
```

---

## 📚 更多文档

- GitHub: https://github.com/yangfei222666-9/AIOS
- 完整文档: 见 `docs/` 目录

---

## 🐛 遇到问题？

1. **端口被占用** - 修改 `config.yaml` 中的 `dashboard.port`
2. **依赖缺失** - 运行 `pip install -r requirements.txt`
3. **其他问题** - 查看 `logs/` 目录的日志文件

---

**版本：** v1.3  
**打包时间：** 2026-02-27 23:37:16  
**作者：** 珊瑚海 + 小九  
