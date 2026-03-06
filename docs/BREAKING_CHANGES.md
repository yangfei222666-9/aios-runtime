# AIOS 破坏性变更说明

## v3.5 - TaskMeta 公共符号语义切换（2026-03-06）

### 变更内容

**TaskMeta 公共符号语义已从 TypedDict 切换为 dataclass。**

### 影响范围

- **模块：** `aios/agent_system/debate_policy_engine.py`
- **符号：** `TaskMeta`
- **变更类型：** 破坏性变更（Breaking Change）

### 变更详情

#### 旧版本（v3.4 及之前）
```python
from typing import TypedDict

class TaskMeta(TypedDict):
    task_id: str
    risk_level: str
    content: str
    task_type: str
    risk_keywords: list
    estimated_impact: str
```

#### 新版本（v3.5+）
```python
from dataclasses import dataclass, field

@dataclass
class TaskMeta:
    """任务元数据（OOP 入口用）"""
    task_id: str
    risk_level: str          # low / medium / high
    content: str = ""
    task_type: str = "code_change"
    risk_keywords: list = field(default_factory=list)
    estimated_impact: str = "medium"
```

### 兼容性处理

**旧 TypedDict 结构已重命名为 `_TaskMetaV2`，仅供内部兼容使用。**

```python
# 内部兼容结构（不推荐外部使用）
class _TaskMetaV2(TypedDict):
    task_id: str
    risk_level: str
    content: str
    task_type: str
    risk_keywords: list
    estimated_impact: str
```

### 迁移指南

#### 场景 1：直接使用 TaskMeta（推荐）

**旧代码：**
```python
from debate_policy_engine import TaskMeta

task: TaskMeta = {
    "task_id": "task-001",
    "risk_level": "high",
    "content": "重构核心模块",
    "task_type": "code_change",
    "risk_keywords": ["refactor", "core"],
    "estimated_impact": "high"
}
```

**新代码：**
```python
from debate_policy_engine import TaskMeta

task = TaskMeta(
    task_id="task-001",
    risk_level="high",
    content="重构核心模块",
    task_type="code_change",
    risk_keywords=["refactor", "core"],
    estimated_impact="high"
)
```

#### 场景 2：需要保持 TypedDict 语义（临时兼容）

**临时方案：**
```python
from debate_policy_engine import _TaskMetaV2 as TaskMeta

task: TaskMeta = {
    "task_id": "task-001",
    "risk_level": "high",
    # ...
}
```

**注意：** `_TaskMetaV2` 仅供内部兼容，未来版本可能移除。

#### 场景 3：使用 DebatePolicyEngine（推荐）

**新代码（无需修改）：**
```python
from debate_policy_engine import DebatePolicyEngine, TaskMeta, HexagramState

engine = DebatePolicyEngine()

task = TaskMeta(
    task_id="task-001",
    risk_level="high",
    content="重构核心模块"
)

state = HexagramState(
    hexagram="坤卦",
    evolution_score=95.0
)

policy = engine.build_debate_policy(state, task)
```

### 为什么要改？

1. **类型安全** - dataclass 提供更强的类型检查
2. **IDE 支持** - 更好的自动补全和重构支持
3. **默认值** - 支持字段默认值，减少样板代码
4. **不可变性** - 可选 `frozen=True` 保证数据不可变
5. **统一风格** - 与 `HexagramState` 等其他数据类保持一致

### 测试验证

**所有测试已通过：**
```bash
cd aios/tests
python test_phase3_exceptions.py
# 4/4 tests passed ✅
```

### 回滚方案

如果遇到兼容性问题，可以临时回滚到 v3.4：

```bash
git checkout v3.4
# 或
pip install aios==3.4
```

### 相关文档

- [debate_policy_engine.py 模块注释](../agent_system/debate_policy_engine.py)
- [Phase 3 集成文档](./PHASE3.md)
- [测试用例](../tests/test_phase3_exceptions.py)

---

**维护者：** 小九 + 珊瑚海  
**创建时间：** 2026-03-06  
**最后更新：** 2026-03-06  
**版本：** v3.5
