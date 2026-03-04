# AIOS - AI Operating System

**让 AI 自己运行、自己看、自己进化。**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-27%2F27-brightgreen.svg)](tests/)

---

## 🚀 10 秒快速开始

```bash
# 1. 下载并解压
unzip AIOS-v1.0.zip
cd aios

# 2. 运行演示（3 个真实场景）
python aios.py demo --scenario 1  # 文件监控 + 自动分类
python aios.py demo --scenario 2  # API 健康检查 + 自动恢复
python aios.py demo --scenario 3  # 日志分析 + 自动生成 Playbook

# 3. 提交任务（自动执行）
python aios.py submit --desc "分析错误日志" --type analysis --priority high

# 4. 查看 Dashboard
python aios.py dashboard
# 打开浏览器访问 http://127.0.0.1:9091
```

---

## 💡 AIOS 是什么？

AIOS 是一个**轻量级的 AI 操作系统**，让你的 AI Agent 能够：

- 🤖 **自主运行** — 自动调度任务，无需人工干预
- 👁️ **自我观测** — 实时监控性能、成本、错误
- 🧬 **自我进化** — 从失败中学习，自动优化策略

**核心特点：**
- ✅ **零依赖** — 纯 Python 标准库，解压即用（0.77 MB）
- ✅ **事件驱动** — 低耦合架构，易于扩展
- ✅ **生产级** — 27 个测试用例，完整错误处理

---

## 🎯 核心功能

### 1. 完整的任务自动化工作流

```bash
# 提交任务
python aios.py submit --desc "重构 scheduler.py" --type code --priority high

# Heartbeat 自动执行（每 30 秒）
python aios.py heartbeat

# 查看任务状态
python aios.py tasks
```

**工作流：**
```
用户提交任务 → 进入队列 → Heartbeat 检测 → 自动执行 → 更新状态 → 记录结果
```

**支持的任务类型：**
- `code` - 代码开发
- `analysis` - 数据分析
- `monitor` - 系统监控
- `refactor` - 代码重构
- `test` - 测试
- `deploy` - 部署
- `research` - 研究

---

### 2. 事件驱动架构

**EventBus** — 所有组件通过事件通信，低耦合

```python
from core.event_bus import get_event_bus
from core.event import create_event

bus = get_event_bus()

# 发布事件
bus.emit(create_event("task.completed", {"task_id": "123"}))

# 订阅事件
bus.subscribe("task.*", lambda event: print(event))
```

**核心组件：**
- **Scheduler** — 智能任务调度（优先级、依赖、并行）
- **Reactor** — 自动响应异常（5 种内置 Playbook）
- **Agent Pool** — 64 个 Agent（27 Learning + 37 Skill）

---

### 3. 完整可观测性

**Tracer + Metrics + Logger** 三件套

```python
from core.tracer import Tracer
from core.metrics import Metrics

# 追踪任务链路
with Tracer.trace("task-123"):
    result = execute_task()

# 记录指标
Metrics.record("task.duration", 1.5)
Metrics.record("task.success", 1)
```

**Dashboard 实时监控：**
- 任务成功率
- 平均响应时间
- 错误率
- 系统健康度

---

### 4. 自我进化闭环

**从失败中学习，自动优化策略**

```
DataCollector（眼睛）→ Evaluator（大脑）→ Quality Gates（刹车）→ Self-Improving Loop（进化）
```

**核心模块：**
1. **DataCollector** — 统一采集所有数据（Event/Task/Agent/Trace/Metric）
2. **Evaluator** — 量化评估（任务成功率、Agent 评分、系统健康度）
3. **Quality Gates** — 三层门禁（L0 自动测试、L1 回归测试、L2 人工审核）
4. **Self-Improving Loop** — 安全自我进化（自动回滚、风险分级）

**健康分数公式：**
```
health_score = (
    success_rate * 60 +      # 60 分：成功率
    (1 - failure_rate) * 30 + # 30 分：低失败率
    (1 - pending_rate) * 10   # 10 分：低待处理率
)
```

---

## 🎬 真实场景演示

### Demo 1: 文件监控 + 自动分类

**场景：** 监控 downloads/ 文件夹，新文件自动分类到对应文件夹

```bash
python aios.py demo --scenario 1
```

**演示效果：**
- 8 个测试文件全部正确分类 ✅
- documents/（2 个）- report.pdf, readme.txt
- images/（1 个）- photo.jpg
- videos/（1 个）- video.mp4
- archives/（1 个）- archive.zip
- code/（1 个）- script.py
- audio/（1 个）- song.mp3
- others/（1 个）- unknown.xyz

**技术亮点：**
- 事件驱动（file.new → file.organized）
- 通配符订阅（file.*）
- 完整日志记录

---

### Demo 2: API 健康检查 + 自动恢复

**场景：** 定期检查 API 端点，失败时自动重试和恢复

```bash
python aios.py demo --scenario 2
```

**演示效果：**
- 3 轮检查，4 个端点 ✅
- 自动重试机制（最多 3 次，指数退避）
- 状态变化检测（healthy ↔ degraded ↔ down）
- 完整日志记录（12 条）

**技术亮点：**
- 健康检查模式（healthy/degraded/down）
- 自动重试 + 指数退避
- 失败计数器
- 状态变化通知

---

### Demo 3: 日志分析 + 自动生成 Playbook

**场景：** 分析错误日志，自动生成修复 Playbook

```bash
python aios.py demo --scenario 3
```

**演示效果：**
- 10 条日志，6 个错误 ✅
- 检测到 4 种错误模式
  - FileNotFoundError（2 次）
  - ConnectionError（2 次）
  - MemoryError（1 次）
  - PermissionError（1 次）
- 生成 4 个 Playbook
  - 2 个自动应用（低风险）
  - 2 个人工审核（中/高风险）

**技术亮点：**
- 模式识别（正则匹配）
- 风险分级（low/medium/high）
- 自动应用策略
- Playbook 持久化（JSON）

---

## 🏗️ 系统架构

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
│  Task Queue (任务队列)                                   │
│    - TaskSubmitter (提交器)                              │
│    - TaskExecutor (执行器)                               │
│    - Heartbeat v5.0 (自动处理)                           │
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

---

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 启动时间 | <1 秒 |
| 内存占用 | ~50 MB |
| 事件延迟 | <10 ms |
| Context 切换 | 736K ops/s |
| Memory.allocate | 3.43M ops/s |
| Memory.stats | 10.96M ops/s（优化后 41.5 倍提升） |
| 自我进化开销 | <1% |

---

## 📚 完整 API 参考

### CLI 命令

```bash
# 系统管理
python aios.py status              # 查看系统状态
python aios.py start               # 启动 AIOS 服务
python aios.py stop                # 停止 AIOS 服务
python aios.py dashboard           # 打开 Dashboard

# 任务管理
python aios.py submit --desc "..." --type code --priority high
python aios.py tasks               # 查看所有任务
python aios.py tasks --status pending  # 查看待处理任务

# 演示和测试
python aios.py demo --scenario 1   # 运行演示
python aios.py test                # 运行测试
python aios.py benchmark           # 性能基准测试

# 监控和维护
python aios.py heartbeat           # 运行心跳（自动执行任务）
python aios.py monitor --duration 5  # 实时监控（5 分钟）
python aios.py analyze             # 性能分析
```

### Python API

```python
# 任务提交
from core.task_submitter import submit_task, list_tasks

task_id = submit_task(
    description="重构 scheduler.py",
    task_type="code",
    priority="high"
)

tasks = list_tasks(status="pending", limit=10)

# 事件总线
from core.event_bus import get_event_bus
from core.event import create_event

bus = get_event_bus()
bus.emit(create_event("task.completed", {"task_id": "123"}))
bus.subscribe("task.*", callback)

# 可观测性
from core.tracer import Tracer
from core.metrics import Metrics

with Tracer.trace("task-123"):
    result = execute_task()

Metrics.record("task.duration", 1.5)
```

---

## 🛠️ 配置说明

### 系统配置

**文件：** `config/system.json`

```json
{
  "scheduler": {
    "max_concurrent_tasks": 5,
    "default_timeout": 60
  },
  "reactor": {
    "enabled": true,
    "max_retries": 3
  },
  "observability": {
    "trace_enabled": true,
    "metrics_enabled": true
  }
}
```

### Agent 配置

**文件：** `agent_system/agents.json`

```json
{
  "agents": [
    {
      "name": "coder",
      "type": "code",
      "priority": "high",
      "timeout": 120
    }
  ]
}
```

---

## 🧪 测试覆盖

**总测试：** 27/27 ✅

| 模块 | 测试数 | 状态 |
|------|--------|------|
| EventBus | 5 | ✅ |
| Scheduler | 6 | ✅ |
| Reactor | 4 | ✅ |
| TaskSubmitter | 5 | ✅ |
| TaskExecutor | 3 | ✅ |
| Heartbeat | 4 | ✅ |

**运行测试：**
```bash
python aios.py test
```

---

## 🗺️ 路线图

### ✅ v1.0（已完成）
- [x] 事件驱动架构（EventBus + Scheduler + Reactor）
- [x] 完整可观测性（Tracer + Metrics + Logger）
- [x] 自我进化闭环（DataCollector + Evaluator + Quality Gates）
- [x] 任务队列系统（TaskSubmitter + TaskExecutor + Heartbeat v5.0）
- [x] 3 个真实场景 Demo
- [x] 零依赖打包（0.77 MB）

### 🚧 v1.1（1-2 周）
- [ ] Dashboard 实时推送（WebSocket）
- [ ] 一键部署脚本（install.sh / install.bat）
- [ ] 集成 sessions_spawn（真实 Agent 执行）
- [ ] 任务重试机制（失败自动重试）

### 📅 v1.2（1-2 月）
- [ ] VM Controller + CloudRouter 集成
- [ ] 多模型支持（OpenAI/Gemini/Ollama）
- [ ] Agent 框架集成（AutoGen/MetaGPT）
- [ ] Agent 市场（社区贡献）

### 🔮 v2.0（3-6 月）
- [ ] 分布式调度（多节点）
- [ ] 向量检索（Memory 模块）
- [ ] 多租户支持（权限隔离）
- [ ] 学术论文发表

---

## ❓ 常见问题

### Q: AIOS 和其他 Agent 框架有什么区别？

**A:** AIOS 的核心优势：
1. **自我进化** - 从失败中学习，自动优化（其他框架没有）
2. **零依赖** - 纯 Python 标准库，解压即用
3. **事件驱动** - 低耦合架构，易于扩展
4. **生产级** - 完整的错误处理、自动回滚、质量门禁

### Q: 如何集成到现有项目？

**A:** AIOS 提供两种集成方式：
1. **CLI 模式** - 通过 `aios.py` 命令行工具
2. **Python API** - 导入 `core` 模块直接调用

### Q: 性能如何？

**A:** 
- 启动时间：<1 秒
- 内存占用：~50 MB
- 事件延迟：<10 ms
- Context 切换：736K ops/s

### Q: 支持哪些平台？

**A:** Windows / Linux / macOS，Python 3.8+

### Q: 如何贡献？

**A:** 欢迎提交 Issue 和 PR！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📖 更多文档

- [安装指南](docs/INSTALL.md)
- [架构设计](ARCHITECTURE.md)
- [API 参考](docs/API.md)
- [教程](docs/TUTORIAL.md)
- [性能优化](OPTIMIZATION_REPORT.md)
- [任务队列集成](TASK_QUEUE_INTEGRATION.md)
- [改进报告](IMPROVEMENT_REPORT.md)

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

**贡献指南：**
1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 打开 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 📞 联系方式

- **GitHub:** [@yangfei222666-9](https://github.com/yangfei222666-9)
- **Telegram:** @shh7799
- **Email:** [your-email@example.com]

---

## 🌟 Star History

如果 AIOS 对你有帮助，请给我们一个 Star ⭐️

---

**AIOS - 让 AI 自己运行、自己看、自己进化。**

*Built with ❤️ by 小九 + 珊瑚海*
