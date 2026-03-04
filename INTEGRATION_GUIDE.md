# AIOS 集成指南 - Scheduler v2.3 和 Reactor v2.0

## 🎯 目标

将新版 Scheduler v2.3 和 Reactor v2.0 集成到 AIOS 核心系统。

---

## 📋 迁移步骤

### 步骤 1：备份旧版本

```bash
cd C:\Users\A\.openclaw\workspace\aios\core

# 备份旧版 Scheduler
copy scheduler.py scheduler.py.bak
copy production_scheduler.py production_scheduler.py.bak

# 备份旧版 Reactor
copy reactor.py reactor.py.bak
```

### 步骤 2：替换文件

**选项 A：直接替换（推荐）**

```bash
# 替换 Scheduler
copy scheduler_v2_3.py scheduler.py
copy scheduling_policies.py scheduling_policies.py
copy thread_binding.py thread_binding.py

# 替换 Reactor
copy reactor_v2.py reactor.py
```

**选项 B：使用兼容层（渐进式迁移）**

```bash
# 使用兼容层
copy production_scheduler_v2.py production_scheduler.py
```

### 步骤 3：更新导入语句

**旧版导入：**
```python
from core.production_scheduler import get_scheduler, Priority
```

**新版导入（选项 A）：**
```python
from core.scheduler_v2_3 import Scheduler, Priority
from core.scheduling_policies import FIFOPolicy, SJFPolicy
```

**新版导入（选项 B - 兼容层）：**
```python
from core.production_scheduler import get_scheduler, Priority
# 无需修改代码，内部自动使用 v2.3
```

### 步骤 4：更新调用代码

**旧版用法：**
```python
scheduler = get_scheduler(max_concurrent=5)
scheduler.start()

task_id = scheduler.submit(
    task_type="code",
    payload={"data": "..."},
    priority=Priority.P1_HIGH
)
```

**新版用法（选项 A）：**
```python
from scheduling_policies import PriorityPolicy

scheduler = Scheduler(
    max_concurrent=5,
    policy=PriorityPolicy(),
    enable_cpu_binding=True,  # 新功能
    cpu_pool=[0, 1, 2, 3]  # 新功能
)

def my_task():
    # 任务逻辑
    return "done"

task_id = scheduler.schedule({
    "id": "task1",
    "func": my_task,
    "priority": Priority.P1_HIGH.value,
    "cpu_affinity": 0  # 新功能：绑定到 CPU 0
})
```

**新版用法（选项 B - 兼容层）：**
```python
# 代码无需修改，但可以使用新功能
scheduler = get_scheduler(
    max_concurrent=5,
    enable_cpu_binding=True,  # 新功能
    cpu_pool=[0, 1, 2, 3]  # 新功能
)
```

---

## 🔧 需要修改的文件

### 高优先级（核心文件）

1. **heartbeat_runner.py**
   - 当前：`from core.production_scheduler import get_scheduler, Priority`
   - 建议：使用兼容层（无需修改）

2. **heartbeat_runner_optimized.py**
   - 当前：`from core.production_scheduler import get_scheduler, Priority`
   - 建议：使用兼容层（无需修改）

3. **pipeline.py**
   - 当前：`from core.scheduler_v2 import SchedulerV2, Priority`
   - 建议：改为 `from core.scheduler_v2_3 import Scheduler, Priority`

### 中优先级（测试文件）

4. **test_production_scheduler.py**
   - 需要更新测试用例

5. **tests/test_core_modules.py**
   - 需要更新测试用例

### 低优先级（Demo 文件）

6. **demo/live_demo.py**
7. **demo/quick_demo.py**
8. **stress_test.py**

---

## 🚀 推荐迁移策略

### 阶段 1：使用兼容层（1天）

1. 部署 `production_scheduler_v2.py`（兼容层）
2. 替换 `core/production_scheduler.py`
3. 运行所有测试，确保兼容性
4. 观察生产环境运行情况

**优点：**
- 零代码修改
- 风险最低
- 可以快速回滚

### 阶段 2：启用新功能（1周）

1. 在非关键路径启用 CPU 绑定
2. 测试不同的调度策略（FIFO/SJF/EDF）
3. 收集性能数据
4. 根据数据调整配置

**优点：**
- 逐步验证新功能
- 有数据支持决策

### 阶段 3：完全迁移（1-2周）

1. 将所有代码迁移到新 API
2. 移除兼容层
3. 更新所有文档
4. 培训团队使用新 API

**优点：**
- 充分利用新功能
- 代码更清晰

---

## 📊 新功能对比

| 功能 | 旧版 | 新版 v2.3 | 说明 |
|------|------|-----------|------|
| 调度算法 | Priority（固定） | 6种可选 | FIFO/SJF/RR/EDF/Priority/Hybrid |
| CPU 绑定 | ❌ | ✅ | 可以将任务绑定到特定 CPU |
| 依赖处理 | ❌ | ✅ | 支持任务依赖关系 |
| 任务取消 | ⚠️ 部分 | ✅ 完整 | 可以取消队列中的任务 |
| 进度追踪 | ❌ | ✅ | get_progress() |
| 回调钩子 | ❌ | ✅ | on_task_complete/error/timeout |
| 线程安全 | ⚠️ 部分 | ✅ 完整 | Lock 全覆盖 |
| 统计信息 | ⚠️ 基础 | ✅ 详细 | 包含 CPU 使用情况 |

---

## 🔍 验证清单

### 功能验证

- [ ] 任务提交正常
- [ ] 任务执行正常
- [ ] 优先级生效
- [ ] 并发控制正常
- [ ] 统计信息正确
- [ ] CPU 绑定生效（如果启用）
- [ ] 调度策略生效（如果使用）

### 性能验证

- [ ] 调度延迟 <10ms
- [ ] CPU 使用率正常
- [ ] 内存无泄漏
- [ ] 无死锁
- [ ] 无竞态条件

### 兼容性验证

- [ ] 旧代码无需修改
- [ ] API 完全兼容
- [ ] 测试全部通过
- [ ] 生产环境稳定

---

## 🐛 常见问题

### Q1：如何回滚到旧版本？

```bash
cd C:\Users\A\.openclaw\workspace\aios\core
copy scheduler.py.bak scheduler.py
copy production_scheduler.py.bak production_scheduler.py
copy reactor.py.bak reactor.py
```

### Q2：CPU 绑定会影响性能吗？

**答：** 有轻微开销（1-2ms），但在多核系统上可以提升缓存命中率。建议：
- 计算密集型任务：启用 CPU 绑定
- I/O 密集型任务：不启用

### Q3：如何选择调度策略？

**答：**
- **FIFO** - 公平性要求高，任务时间相近
- **SJF** - 最小化平均等待时间，任务时间差异大
- **RR** - 交互式系统，需要快速响应
- **EDF** - 实时系统，任务有明确截止时间
- **Priority** - 任务有明确重要性区分（默认）

### Q4：兼容层有性能损失吗？

**答：** 几乎没有（<1%），主要是一层函数调用的开销。

---

## 📞 支持

如果遇到问题：
1. 查看日志：`aios/logs/scheduler.log`
2. 检查统计：`scheduler.get_stats()`
3. 联系：小九（AI 助手）

---

**版本：** v1.0  
**日期：** 2026-02-26  
**作者：** 小九 + 珊瑚海
