# AIOS API 文档

## 核心模块

### Planner（智能规划）**NEW!**

#### 初始化

```python
from core.planner import Planner
from pathlib import Path

workspace = Path("/path/to/workspace")
planner = Planner(workspace)
```

#### 规划任务

```python
plan = planner.plan(
    task="实现 Memory 模块",
    strategy="auto"  # auto/sequential/parallel/dag
)

print(f"任务ID: {plan.task_id}")
print(f"子任务数: {len(plan.subtasks)}")
print(f"执行策略: {plan.strategy}")

for subtask in plan.subtasks:
    print(f"- {subtask.description} ({subtask.type})")
    print(f"  依赖: {subtask.dependencies}")
    print(f"  预估耗时: {subtask.estimated_time}s")
```

#### 加载计划

```python
plan = planner.load_plan(task_id)
if plan:
    print(f"原始任务: {plan.original_task}")
    print(f"子任务数: {len(plan.subtasks)}")
```

#### 更新子任务状态

```python
planner.update_subtask_status(
    task_id="plan_123",
    subtask_id="subtask_1",
    status="completed",
    result="设计完成"
)
```

#### 获取下一批可执行子任务

```python
next_tasks = planner.get_next_subtasks(task_id)
for task in next_tasks:
    print(f"可执行: {task.description}")
```

---

### Scheduler v3.0（集成 Planning）**NEW!**

#### 初始化

```python
from core.scheduler import Scheduler
from pathlib import Path

workspace = Path("/path/to/workspace")
scheduler = Scheduler(
    max_concurrent=5,      # 最大并发任务数
    default_timeout=30,    # 默认超时（秒）
    workspace=workspace
)
```

#### 基础任务调度

```python
def my_task():
    return "Task completed"

scheduler.schedule({
    "id": "task_1",
    "func": my_task,
    "depends_on": []  # 依赖的任务 ID 列表
})
```

#### 带依赖的任务调度

```python
def task_a():
    return "A done"

def task_b():
    return "B done"

scheduler.schedule({"id": "A", "func": task_a})
scheduler.schedule({"id": "B", "func": task_b, "depends_on": ["A"]})
```

#### 智能规划调度（自动拆解）

```python
from core.planner import SubTask

def executor(subtask: SubTask):
    print(f"执行: {subtask.description}")
    # 执行子任务
    return f"{subtask.description} - 完成"

def on_complete(plan):
    print(f"Plan {plan.task_id} 完成！")
    for st in plan.subtasks:
        print(f"- {st.description}: {st.status}")

plan_id = scheduler.schedule_with_planning(
    task_description="对比 AIOS 和标准 Agent 架构",
    executor=executor,
    callback=on_complete,
    strategy="auto"  # auto/sequential/parallel/dag
)
```

#### 查看 Plan 状态

```python
status = scheduler.get_plan_status(plan_id)
print(f"任务ID: {status['task_id']}")
print(f"原始任务: {status['original_task']}")
print(f"执行策略: {status['strategy']}")
print(f"总任务数: {status['total']}")
print(f"已完成: {status['completed']}")
print(f"失败: {status['failed']}")
print(f"运行中: {status['running']}")
print(f"待执行: {status['pending']}")
print(f"进度: {status['progress']}")  # "3/5"
```

#### 优雅关闭

```python
scheduler.shutdown(wait=True)
```

---

### EventBus（事件总线）

#### 获取实例

```python
from core.event_bus import get_event_bus

bus = get_event_bus()
```

#### 发布事件

```python
from core.event import create_event, EventType

event = create_event(
    event_type=EventType.RESOURCE_HIGH,
    data={"resource": "cpu", "value": 85}
)
bus.emit(event)
```

#### 订阅事件

```python
def handler(event):
    print(f"收到事件: {event.type}")

bus.subscribe(EventType.RESOURCE_HIGH, handler)
```

#### 取消订阅

```python
bus.unsubscribe(EventType.RESOURCE_HIGH, handler)
```

---

### Reactor（自动修复）

#### 初始化

```python
from core.production_reactor import ProductionReactor

reactor = ProductionReactor()
```

#### 加载 Playbook

```python
reactor.load_playbooks("playbooks/")
```

#### 处理事件

```python
result = reactor.handle_event(event)
if result:
    print(f"修复成功: {result}")
else:
    print("未找到匹配的 Playbook")
```

---

### ScoreEngine（评分引擎）

#### 初始化

```python
from core.score_engine import ScoreEngine

engine = ScoreEngine()
```

#### 获取评分

```python
score = engine.get_score()
print(f"Evolution Score: {score:.2f}")
```

#### 获取详细指标

```python
metrics = engine.get_metrics()
print(f"任务成功率: {metrics['task_success_rate']:.2%}")
print(f"修复率: {metrics['fix_rate']:.2%}")
print(f"运行时间: {metrics['uptime_hours']:.1f}h")
```

---

### Agent System（Agent 管理）

#### 初始化

```python
from agent_system.auto_dispatcher import AutoDispatcher

dispatcher = AutoDispatcher()
dispatcher.start()
```

#### 调度任务

```python
dispatcher.dispatch_task({
    "type": "worker",
    "params": {
        "task": "analyze_logs",
        "priority": "high"
    }
})
```

#### 获取 Agent 状态

```python
status = dispatcher.get_status()
print(f"活跃 Agent: {status['active_agents']}")
print(f"待处理任务: {status['pending_tasks']}")
```

---

## 数据结构

### SubTask（子任务）

```python
@dataclass
class SubTask:
    id: str                      # 子任务 ID
    description: str             # 任务描述
    type: str                    # 任务类型（code/analysis/monitor/research/design）
    priority: str                # 优先级（high/normal/low）
    dependencies: List[str]      # 依赖的子任务 ID
    estimated_time: int          # 预估耗时（秒）
    status: str = "pending"      # 状态（pending/running/completed/failed）
    result: Optional[str] = None # 执行结果
    created_at: float = 0.0      # 创建时间
```

### Plan（执行计划）

```python
@dataclass
class Plan:
    task_id: str                 # 任务 ID
    original_task: str           # 原始任务描述
    subtasks: List[SubTask]      # 子任务列表
    strategy: str                # 执行策略（sequential/parallel/dag）
    created_at: float = 0.0      # 创建时间
```

### Event（事件）

```python
@dataclass
class Event:
    id: str                      # 事件 ID
    type: EventType              # 事件类型
    data: Dict[str, Any]         # 事件数据
    timestamp: float             # 时间戳
    source: str                  # 事件源
```

---

## 完整示例

### 示例1：智能任务规划

```python
from core.planner import Planner
from core.scheduler import Scheduler
from pathlib import Path

# 初始化
workspace = Path("/path/to/workspace")
planner = Planner(workspace)
scheduler = Scheduler(max_concurrent=3, workspace=workspace)

# 定义执行器
def executor(subtask):
    print(f"执行: {subtask.description}")
    # 实际执行逻辑
    return f"{subtask.description} - 完成"

# 定义回调
def on_complete(plan):
    print(f"Plan {plan.task_id} 完成！")
    for st in plan.subtasks:
        print(f"- {st.description}: {st.status}")

# 调度任务（自动拆解）
plan_id = scheduler.schedule_with_planning(
    "实现 Memory 模块",
    executor=executor,
    callback=on_complete
)

# 等待完成
import time
time.sleep(10)

# 查看状态
status = scheduler.get_plan_status(plan_id)
print(f"进度: {status['progress']}")

# 关闭
scheduler.shutdown()
```

### 示例2：事件驱动自动修复

```python
from core.event_bus import get_event_bus
from core.event import create_event, EventType
from core.production_reactor import ProductionReactor

# 初始化
bus = get_event_bus()
reactor = ProductionReactor()
reactor.load_playbooks("playbooks/")

# 订阅事件
def auto_fix(event):
    result = reactor.handle_event(event)
    if result:
        print(f"自动修复成功: {result}")

bus.subscribe(EventType.RESOURCE_HIGH, auto_fix)

# 发布事件
event = create_event(
    EventType.RESOURCE_HIGH,
    {"resource": "cpu", "value": 85}
)
bus.emit(event)
```

---

## 常见问题

### Q: 如何自定义任务拆解规则？

A: 修改 `planner.py` 中的 `_decompose_with_cot()` 方法，添加新的拆解规则。

### Q: 如何调整并发数？

A: 在初始化 Scheduler 时设置 `max_concurrent` 参数。

### Q: 如何处理任务超时？

A: 在初始化 Scheduler 时设置 `default_timeout` 参数（秒）。

### Q: 如何查看任务执行日志？

A: 查看 `aios/plans/` 目录下的 JSON 文件。

---

**版本：** v1.1  
**最后更新：** 2026-02-26
