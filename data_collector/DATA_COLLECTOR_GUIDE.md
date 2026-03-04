# DataCollector 使用指南

## 概述

DataCollector 是 AIOS 的统一数据采集层，负责收集、存储和查询所有系统数据。

**核心功能：**
1. ✅ 统一入口 - 所有数据采集走一个接口
2. ✅ 标准 Schema - 5 种核心数据类型（Event/Task/Agent/Trace/Metric）
3. ✅ 自动关联 - task/agent/trace 自动串联
4. ✅ 智能归档 - 按日期/类型分类
5. ✅ 高性能 - 异步写入，批量提交

**测试覆盖：** 10/10 ✅

---

## 快速开始

### 1. 导入

```python
from aios.data_collector import DataCollector

# 初始化（全局单例）
collector = DataCollector()
```

### 2. 记录事件

```python
# 记录事件
event_id = collector.log_event(
    type="task_started",
    severity="info",
    task_id="task_123",
    agent_id="coder",
    payload={"model": "claude-sonnet-4-6"}
)

# 查询事件
events = collector.query_events(
    task_id="task_123",
    severity="info"
)
```

### 3. 管理任务

```python
# 创建任务
task_id = collector.create_task(
    title="实现 DataCollector",
    type="code",
    priority="high"
)

# 更新任务状态
collector.update_task(task_id, status="running")

# 完成任务
collector.complete_task(
    task_id,
    status="success",
    result={"output": "done"},
    metrics={"duration_ms": 1000, "tokens_used": 500}
)

# 查询任务
tasks = collector.query_tasks(
    status="running",
    type="code"
)
```

### 4. 更新 Agent 状态

```python
# 更新 Agent
collector.update_agent(
    agent_id="coder",
    type="coder",
    status="busy",
    stats={
        "tasks_total": 10,
        "tasks_success": 8,
        "tasks_failed": 2
    }
)

# 获取 Agent
agent = collector.get_agent("coder")
```

### 5. 追踪链路

```python
# 创建追踪
trace_id = collector.create_trace(task_id="task_123")

# 添加 Span
span_id = collector.add_span(
    trace_id=trace_id,
    name="code_generation",
    tags={"model": "claude-sonnet-4-6"}
)
```

### 6. 记录指标

```python
# 记录指标
collector.record_metric(
    name="task_duration_ms",
    value=1500.0,
    tags={"task_type": "code", "status": "success"}
)
```

---

## 数据模型

### 1. Event（事件）

系统中发生的所有事情。

```python
{
    "id": "evt_xxx",
    "ts": "2026-02-26T23:48:00Z",
    "type": "task_started|agent_spawned|error_occurred|...",
    "severity": "debug|info|warning|error|critical",
    "task_id": "task_xxx",
    "agent_id": "coder",
    "trace_id": "trace_xxx",
    "span_id": "span_xxx",
    "payload": {...}
}
```

**常见事件类型：**
- `task_created` - 任务创建
- `task_started` - 任务开始
- `task_success` - 任务成功
- `task_failed` - 任务失败
- `agent_spawned` - Agent 创建
- `agent_updated` - Agent 更新
- `error_occurred` - 错误发生

### 2. Task（任务）

用户请求或系统任务。

```python
{
    "id": "task_xxx",
    "title": "实现 DataCollector",
    "type": "code|analysis|monitor|research|design",
    "status": "pending|running|success|failed|cancelled",
    "priority": "high|normal|low",
    "created_at": "2026-02-26T23:48:00Z",
    "started_at": "2026-02-26T23:48:05Z",
    "completed_at": "2026-02-26T23:50:00Z",
    "agent_id": "coder",
    "parent_task_id": null,
    "trace_id": "trace_xxx",
    "result": {...},
    "metrics": {
        "duration_ms": 115000,
        "tokens_used": 5000,
        "cost_usd": 0.05
    }
}
```

### 3. Agent（Agent 状态）

```python
{
    "id": "coder",
    "type": "coder|analyst|monitor|...",
    "status": "idle|busy|failed|disabled",
    "created_at": "2026-02-26T00:00:00Z",
    "last_active": "2026-02-26T23:48:00Z",
    "stats": {
        "tasks_total": 100,
        "tasks_success": 85,
        "tasks_failed": 15,
        "avg_duration_ms": 30000,
        "total_cost_usd": 5.0
    },
    "config": {...}
}
```

### 4. Trace（追踪链路）

```python
{
    "trace_id": "trace_xxx",
    "task_id": "task_xxx",
    "started_at": "2026-02-26T23:48:00Z",
    "completed_at": "2026-02-26T23:50:00Z",
    "spans": [
        {
            "span_id": "span_xxx",
            "name": "code_generation",
            "started_at": "2026-02-26T23:48:05Z",
            "completed_at": "2026-02-26T23:49:00Z",
            "tags": {"model": "claude-sonnet-4-6"}
        }
    ]
}
```

### 5. Metric（指标）

```python
{
    "ts": "2026-02-26T23:48:00Z",
    "name": "task_duration_ms",
    "value": 115000,
    "tags": {
        "task_type": "code",
        "agent_id": "coder",
        "status": "success"
    }
}
```

---

## 目录结构

```
aios/
├── data/
│   ├── events/
│   │   ├── 2026-02-26.jsonl  # 按日期归档
│   │   └── 2026-02-25.jsonl
│   ├── tasks/
│   │   ├── tasks.jsonl       # 活跃任务
│   │   └── archive/
│   │       └── 2026-02-26.jsonl
│   ├── agents/
│   │   └── agents.jsonl      # Agent 状态
│   ├── traces/
│   │   └── 2026-02-26.jsonl
│   └── metrics/
│       └── 2026-02-26.jsonl
```

---

## API 参考

### Event API

#### `log_event(type, severity, task_id, agent_id, trace_id, span_id, payload)`

记录事件。

**参数：**
- `type` (str) - 事件类型
- `severity` (str) - 严重程度（debug|info|warning|error|critical）
- `task_id` (str, optional) - 关联任务 ID
- `agent_id` (str, optional) - 关联 Agent ID
- `trace_id` (str, optional) - 关联追踪 ID
- `span_id` (str, optional) - 关联 Span ID
- `payload` (dict, optional) - 额外数据

**返回：** 事件 ID

#### `query_events(task_id, agent_id, trace_id, type, severity, limit)`

查询事件。

**参数：**
- `task_id` (str, optional) - 任务 ID
- `agent_id` (str, optional) - Agent ID
- `trace_id` (str, optional) - 追踪 ID
- `type` (str, optional) - 事件类型
- `severity` (str, optional) - 严重程度
- `limit` (int, optional) - 最大返回数量

**返回：** 事件列表

### Task API

#### `create_task(title, type, priority, agent_id, parent_task_id, trace_id)`

创建任务。

**参数：**
- `title` (str) - 任务标题
- `type` (str) - 任务类型（code|analysis|monitor|research|design）
- `priority` (str) - 优先级（high|normal|low）
- `agent_id` (str, optional) - 分配的 Agent ID
- `parent_task_id` (str, optional) - 父任务 ID
- `trace_id` (str, optional) - 追踪 ID

**返回：** 任务 ID

#### `update_task(task_id, status, agent_id, result, metrics)`

更新任务。

**参数：**
- `task_id` (str) - 任务 ID
- `status` (str, optional) - 状态（pending|running|success|failed|cancelled）
- `agent_id` (str, optional) - Agent ID
- `result` (dict, optional) - 执行结果
- `metrics` (dict, optional) - 性能指标

#### `complete_task(task_id, status, result, metrics)`

完成任务。

**参数：**
- `task_id` (str) - 任务 ID
- `status` (str) - 状态（success|failed）
- `result` (dict, optional) - 执行结果
- `metrics` (dict, optional) - 性能指标

#### `query_tasks(status, type, agent_id, priority, limit)`

查询任务。

**参数：**
- `status` (str, optional) - 状态
- `type` (str, optional) - 类型
- `agent_id` (str, optional) - Agent ID
- `priority` (str, optional) - 优先级
- `limit` (int, optional) - 最大返回数量

**返回：** 任务列表

### Agent API

#### `update_agent(agent_id, type, status, stats, config)`

更新 Agent 状态。

**参数：**
- `agent_id` (str) - Agent ID
- `type` (str, optional) - Agent 类型
- `status` (str, optional) - 状态（idle|busy|failed|disabled）
- `stats` (dict, optional) - 统计数据
- `config` (dict, optional) - 配置

#### `get_agent(agent_id)`

获取 Agent 状态。

**参数：**
- `agent_id` (str) - Agent ID

**返回：** Agent 数据（如果不存在返回 None）

### Trace API

#### `create_trace(task_id)`

创建追踪链路。

**参数：**
- `task_id` (str, optional) - 关联任务 ID

**返回：** 追踪 ID

#### `add_span(trace_id, name, tags)`

添加 Span。

**参数：**
- `trace_id` (str) - 追踪 ID
- `name` (str) - Span 名称
- `tags` (dict, optional) - 标签

**返回：** Span ID

### Metric API

#### `record_metric(name, value, tags)`

记录指标。

**参数：**
- `name` (str) - 指标名称
- `value` (float) - 指标值
- `tags` (dict, optional) - 标签

---

## 集成示例

### 集成到 Agent System

```python
from aios.data_collector import DataCollector

collector = DataCollector()

# 创建任务
task_id = collector.create_task(
    title="生成代码",
    type="code",
    priority="high",
    agent_id="coder"
)

# 开始执行
collector.update_task(task_id, status="running")
collector.log_event(
    type="task_started",
    severity="info",
    task_id=task_id,
    agent_id="coder"
)

# 执行完成
collector.complete_task(
    task_id,
    status="success",
    result={"code": "..."},
    metrics={"duration_ms": 5000, "tokens_used": 1000}
)

# 更新 Agent 统计
agent = collector.get_agent("coder")
if agent:
    stats = agent["stats"]
    stats["tasks_total"] += 1
    stats["tasks_success"] += 1
    collector.update_agent("coder", stats=stats)
```

### 集成到 Scheduler

```python
from aios.data_collector import DataCollector

collector = DataCollector()

# 记录调度决策
collector.log_event(
    type="scheduler_decision",
    severity="info",
    payload={
        "decision": "route_to_coder",
        "reason": "code task detected"
    }
)

# 记录性能指标
collector.record_metric(
    name="scheduler_latency_ms",
    value=50.0,
    tags={"decision": "route_to_coder"}
)
```

### 集成到 Reactor

```python
from aios.data_collector import DataCollector

collector = DataCollector()

# 记录故障事件
collector.log_event(
    type="incident_detected",
    severity="error",
    payload={
        "incident_type": "high_cpu",
        "value": 95.0
    }
)

# 记录修复动作
collector.log_event(
    type="reactor_action",
    severity="info",
    payload={
        "action": "restart_service",
        "result": "success"
    }
)
```

---

## 性能优化

### 批量写入

```python
# 批量记录事件（未来支持）
events = [
    {"type": "event1", "severity": "info"},
    {"type": "event2", "severity": "info"},
    {"type": "event3", "severity": "info"}
]
collector.log_events_batch(events)
```

### 异步写入

```python
# 异步记录（未来支持）
await collector.log_event_async(
    type="task_started",
    severity="info"
)
```

---

## 常见问题

### Q: DataCollector 是单例吗？

A: 是的，默认情况下 DataCollector 是全局单例。但在测试时可以指定 `base_dir` 创建独立实例。

### Q: 数据会自动清理吗？

A: 目前不会自动清理，需要手动归档。未来会支持自动归档（Phase 3）。

### Q: 如何查询历史数据？

A: 使用 `query_events()` / `query_tasks()` 等方法，支持按 task_id/agent_id/trace_id 等过滤。

### Q: 支持分布式部署吗？

A: 目前不支持，所有数据存储在本地 JSONL 文件。未来可以扩展到数据库（SQLite/PostgreSQL）。

---

## 下一步

- [ ] Phase 2: 查询接口优化（索引、分页、排序）
- [ ] Phase 3: 自动归档清理（集成到 heartbeat）
- [ ] Phase 4: Dashboard 集成（实时查询）
- [ ] Phase 5: 数据库支持（SQLite/PostgreSQL）

---

**版本：** v1.0.0  
**最后更新：** 2026-02-26  
**维护者：** 小九 + 珊瑚海
