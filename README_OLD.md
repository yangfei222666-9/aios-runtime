# AIOS - AI Operating System

**让 AI 自己运行、自己看、自己进化。**

## 30 秒快速了解

AIOS 是一个轻量级的 AI 操作系统，让你的 AI Agent 能够：
- 🤖 **自主运行** — 自动调度任务，无需人工干预
- 👁️ **自我观测** — 实时监控性能、成本、错误
- 🧬 **自我进化** — 从失败中学习，自动优化策略

**零依赖，解压即用。**

## 快速开始

```bash
# 1. 下载并解压
unzip AIOS-v1.0.zip
cd aios

# 2. 运行演示
python aios.py demo

# 3. 查看 Dashboard
python aios.py dashboard
# 打开浏览器访问 http://127.0.0.1:8888
```

## 核心特性

### 🎯 事件驱动架构
- **EventBus** — 所有组件通过事件通信，低耦合
- **Scheduler** — 智能任务调度（优先级、依赖、并行）
- **Reactor** — 自动响应异常（5 种内置 Playbook）

### 📊 完整可观测性
- **Tracer** — 分布式追踪（任务链路）
- **Metrics** — 实时指标（成功率、耗时、成本）
- **Logger** — 结构化日志（按日期归档）

### 🧬 自我进化闭环
```
DataCollector（眼睛）→ Evaluator（大脑）→ Quality Gates（刹车）→ Self-Improving Loop（进化）
```

- **DataCollector** — 统一采集所有数据（Event/Task/Agent/Trace/Metric）
- **Evaluator** — 量化评估（任务成功率、Agent 评分、系统健康度）
- **Quality Gates** — 三层门禁（L0 自动测试、L1 回归测试、L2 人工审核）
- **Self-Improving Loop** — 安全自我进化（自动回滚、风险分级）

## 真实场景演示

### 场景 1：文件监控 + 自动修复
```python
# 监控配置文件变化
python aios.py monitor --path config.json

# 当文件被误删时，AIOS 自动：
# 1. 检测到 FileNotFoundError
# 2. 触发 Reactor（file_recovery Playbook）
# 3. 从备份恢复文件
# 4. 记录事件到 DataCollector
# 5. 评估修复效果（Evaluator）
```

### 场景 2：API 健康检查
```python
# 定期检查 API 健康度
python aios.py health-check --url https://api.example.com

# 当 API 失败时，AIOS 自动：
# 1. 检测到 HTTP 500 错误
# 2. 触发 Reactor（api_retry Playbook）
# 3. 重试 3 次（指数退避）
# 4. 失败后降级到备用 API
# 5. 通知管理员
```

### 场景 3：日志分析 + 自动生成 Playbook
```python
# 分析日志，发现错误模式
python aios.py analyze-logs --path logs/

# AIOS 自动：
# 1. 扫描日志，提取错误模式
# 2. 生成新的 Playbook（基于历史修复记录）
# 3. 通过 Quality Gates 验证
# 4. 自动应用到 Reactor
```

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      AIOS Core                          │
├─────────────────────────────────────────────────────────┤
│  EventBus (事件总线)                                     │
│    ↓                                                     │
│  Scheduler (调度器) → Agent Pool (64 Agents)            │
│    ↓                                                     │
│  Reactor (反应器) → Playbook Library (5 Playbooks)      │
├─────────────────────────────────────────────────────────┤
│  Observability (可观测性)                                │
│    - Tracer (追踪)                                       │
│    - Metrics (指标)                                      │
│    - Logger (日志)                                       │
├─────────────────────────────────────────────────────────┤
│  Self-Improving Loop (自我进化)                          │
│    - DataCollector (数据采集)                            │
│    - Evaluator (量化评估)                                │
│    - Quality Gates (质量门禁)                            │
│    - Evolution Engine (进化引擎)                         │
└─────────────────────────────────────────────────────────┘
```

## 技术亮点

### 1. 零依赖
- 纯 Python 标准库
- 无需安装第三方包
- 解压即用（0.77 MB）

### 2. 模块化设计
- 每个组件独立可测试
- 清晰的接口定义
- 易于扩展

### 3. 生产级质量
- 27 个测试用例（全部通过）
- 完整的错误处理
- 自动回滚机制

## 性能指标

- **启动时间：** <1 秒
- **内存占用：** ~50 MB
- **事件延迟：** <10 ms
- **自我进化开销：** <1%

## 系统要求

- Python 3.8+
- Windows / Linux / macOS
- 无需 GPU

## 文档

- [安装指南](docs/INSTALL.md)
- [API 参考](docs/API.md)
- [教程](docs/TUTORIAL.md)
- [架构设计](docs/ARCHITECTURE.md)

## 路线图

### v1.1（1-2 周）
- [ ] Dashboard 实时推送（WebSocket）
- [ ] 一键部署脚本（install.sh / install.bat）
- [ ] 更多真实场景 demo

### v1.2（1-2 月）
- [ ] Agent 市场（社区贡献 Agent 模板）
- [ ] 多租户支持（权限隔离、资源配额）
- [ ] VM Controller + CloudRouter 集成

### v2.0（3-6 月）
- [ ] 分布式调度（多节点）
- [ ] 向量检索（Memory 模块）
- [ ] 学术论文发表

## 贡献

欢迎提交 Issue 和 PR！

## 许可证

MIT License

## 联系方式

- GitHub: [@yangfei222666-9](https://github.com/yangfei222666-9)
- Telegram: @shh7799

---

**AIOS - 让 AI 自己运行、自己看、自己进化。**
