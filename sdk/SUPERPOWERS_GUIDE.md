# Superpowers Mode - 使用指南

## 概述

**Superpowers Mode** 是 AIOS 的快速执行模式，跳过详细规划，直接执行任务。

**灵感来源：** Claude Code 取消 Plan 模式，直接用 Superpowers

**核心思路：** 把所有非代码执行的思考工作交给 AI，人类只负责高层设计

## 使用场景

### ✅ 适合 Superpowers Mode
- 简单任务（不需要复杂规划）
- 快速原型（先跑起来再优化）
- 探索性任务（不确定最佳路径）
- 紧急修复（快速响应）

### ❌ 不适合 Superpowers Mode
- 复杂任务（需要多步协调）
- 关键任务（需要详细规划和审核）
- 高风险操作（需要人工确认）

## 快速开始

### 1. 基础用法

```python
from aios.sdk.superpowers import superpower

# 最简单的用法
result = superpower("创建一个 Flask API")

# 带上下文
result = superpower(
    "分析日志文件",
    context={"file": "app.log"}
)

# 自定义参数
result = superpower(
    "生成测试数据",
    max_steps=20,      # 最大步数
    timeout=600        # 超时时间（秒）
)
```

### 2. 完整示例

```python
from aios.sdk.superpowers import SuperpowersMode

# 创建实例
mode = SuperpowersMode()

# 执行任务
result = mode.execute(
    task="创建一个简单的 Web 服务",
    context={
        "port": 8080,
        "routes": ["/", "/api/health"]
    },
    max_steps=10,
    timeout=300
)

# 检查结果
if result["success"]:
    print(f"✅ 任务完成（{result['steps']} 步，{result['elapsed']:.2f}秒）")
    print(f"结果：{result['result']}")
else:
    print(f"❌ 任务失败：{result['error']}")
```

## 对比：Planning Mode vs Superpowers Mode

| 特性 | Planning Mode | Superpowers Mode |
|------|---------------|------------------|
| **规划** | 先规划再执行 | 直接执行 |
| **速度** | 较慢（需要规划） | 快速（跳过规划） |
| **适用场景** | 复杂任务 | 简单任务 |
| **可追溯性** | 高（有详细计划） | 中（有执行历史） |
| **灵活性** | 低（按计划执行） | 高（动态调整） |
| **风险** | 低（有规划保障） | 中（可能偏离目标） |

## 工作原理

```
用户输入任务
    ↓
分析任务 → 识别需要的工具
    ↓
直接调用工具（无需生成详细计划）
    ↓
根据结果决定下一步（动态调整）
    ↓
重复直到完成或超时
    ↓
返回结果
```

## 核心优势

1. **快速响应** - 跳过规划，直接执行
2. **动态调整** - 根据实际情况调整策略
3. **简单易用** - 一行代码搞定
4. **完整记录** - 所有执行步骤都记录到 DataCollector

## 数据收集

所有 Superpowers 任务都会自动记录到 DataCollector：

```python
# 查询任务历史
from aios.data_collector.collector import DataCollector

collector = DataCollector()
tasks = collector.query_tasks(agent_id="superpowers")

for task in tasks:
    print(f"任务：{task['description']}")
    print(f"状态：{task['status']}")
    print(f"耗时：{task['elapsed_ms']}ms")
```

## 集成到 AIOS

### 1. 在 Scheduler 中使用

```python
from aios.core.scheduler import Scheduler
from aios.sdk.superpowers import superpower

scheduler = Scheduler()

# 添加 Superpowers 任务
scheduler.submit(
    agent_id="superpowers",
    task="快速修复 bug",
    mode="superpowers"  # 指定模式
)
```

### 2. 在 Agent 中使用

```python
from aios.sdk.superpowers import SuperpowersMode

class MyAgent:
    def __init__(self):
        self.superpowers = SuperpowersMode()
    
    def handle_urgent_task(self, task: str):
        # 紧急任务用 Superpowers 模式
        return self.superpowers.execute(task)
```

## 配置

在 `aios/config.json` 中配置默认参数：

```json
{
  "superpowers": {
    "max_steps": 10,
    "timeout": 300,
    "enable_logging": true,
    "fallback_to_planning": false
  }
}
```

## 最佳实践

### ✅ 推荐做法
1. **简单任务优先** - 复杂任务先拆分
2. **设置合理超时** - 避免无限循环
3. **检查执行结果** - 确认任务完成
4. **记录执行历史** - 方便调试和优化

### ❌ 避免做法
1. **不要用于关键任务** - 缺少规划保障
2. **不要设置过大的 max_steps** - 可能导致资源浪费
3. **不要忽略错误** - 及时处理失败情况

## 未来计划

- [ ] 集成 LLM 做决策（替换简化版 ReAct）
- [ ] 支持多工具并行执行
- [ ] 自动学习最佳执行路径
- [ ] 与 Planning Mode 自动切换

## 示例场景

### 场景 1：快速原型

```python
# 快速创建一个 API 原型
result = superpower("""
创建一个简单的 REST API：
- GET /users - 返回用户列表
- POST /users - 创建新用户
- 使用内存存储（不需要数据库）
""")
```

### 场景 2：紧急修复

```python
# 快速修复生产问题
result = superpower(
    "修复 API 超时问题",
    context={
        "error_log": "connection timeout after 30s",
        "endpoint": "/api/data"
    }
)
```

### 场景 3：探索性任务

```python
# 探索新技术
result = superpower(
    "尝试用 FastAPI 重写现有 Flask API",
    max_steps=20
)
```

## 总结

**Superpowers Mode** 是 AIOS 的快速执行模式，适合简单任务和快速原型。

**核心理念：** 把思考工作交给 AI，人类只负责高层设计。

**使用建议：** 简单任务用 Superpowers，复杂任务用 Planning。

---

**版本：** v1.0  
**最后更新：** 2026-02-27  
**维护者：** 小九 + 珊瑚海
