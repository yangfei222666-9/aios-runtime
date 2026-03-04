# Evaluator 使用指南

## 概述

Evaluator 是 AIOS 的量化评估系统，负责评估任务、Agent 和系统的运行质量。

**核心功能：**
1. ✅ 任务评估 - 成功率、耗时、成本
2. ✅ Agent 评估 - 性能、稳定性、效率
3. ✅ 系统评估 - 健康度、Evolution Score、错误率
4. ✅ 改进评估 - Self-Improving Loop 效果验证
5. ✅ 报告生成 - 完整的评估报告

**测试覆盖：** 7/7 ✅

---

## 快速开始

### 1. 导入

```python
from aios.data_collector.evaluator import Evaluator

# 初始化
evaluator = Evaluator()
```

### 2. 评估任务

```python
# 评估最近 24 小时的任务
result = evaluator.evaluate_tasks(time_window_hours=24)

print(f"总任务数: {result['total']}")
print(f"成功率: {result['success_rate']:.2%}")
print(f"平均耗时: {result['avg_duration_ms']:.0f} ms")
```

### 3. 评估 Agent

```python
# 评估单个 Agent
result = evaluator.evaluate_agent("coder")

print(f"Agent: {result['agent_id']}")
print(f"评分: {result['score']:.2f}/100")
print(f"等级: {result['grade']}")
```

### 4. 评估系统

```python
# 评估系统健康度
result = evaluator.evaluate_system(time_window_hours=24)

print(f"健康评分: {result['health_score']:.2f}/100")
print(f"等级: {result['grade']}")
```

### 5. 生成报告

```python
# 生成完整评估报告
report = evaluator.generate_report(time_window_hours=24)

print(f"报告时间: {report['timestamp']}")
print(f"系统健康度: {report['system']['health_score']:.2f}/100")
```

---

## 评估维度

### 1. 任务评估（evaluate_tasks）

**评估指标：**
- 总任务数
- 成功任务数
- 失败任务数
- 成功率（success_rate）
- 平均耗时（avg_duration_ms）
- 平均成本（avg_cost_usd）

**示例输出：**
```json
{
  "total": 10,
  "success": 8,
  "failed": 2,
  "success_rate": 0.8,
  "avg_duration_ms": 5500.0,
  "avg_cost_usd": 0.05,
  "time_window_hours": 24,
  "task_type": "code"
}
```

### 2. Agent 评估（evaluate_agent）

**评估指标：**
- 成功率（success_rate）
- 平均耗时（avg_duration_ms）
- 总成本（total_cost_usd）
- 综合评分（score，0-100）
- 等级（grade，S/A/B/C/D/F）

**评分算法：**
```
综合评分 = 成功率 * 60% + 速度评分 * 20% + 成本评分 * 20%

速度评分：
- 30s 以内 = 20 分
- 60s 以上 = 0 分
- 线性插值

成本评分：
- $0.1 以内 = 20 分
- $1 以上 = 0 分
- 线性插值
```

**等级划分：**
- S: 90-100
- A: 80-89
- B: 70-79
- C: 60-69
- D: 50-59
- F: 0-49

**示例输出：**
```json
{
  "agent_id": "coder",
  "status": "idle",
  "stats": {
    "tasks_total": 10,
    "tasks_success": 8,
    "tasks_failed": 2,
    "avg_duration_ms": 5500,
    "total_cost_usd": 0.05
  },
  "success_rate": 0.8,
  "avg_duration_ms": 5500,
  "total_cost_usd": 0.05,
  "score": 84.97,
  "grade": "A"
}
```

### 3. 系统评估（evaluate_system）

**评估指标：**
- 健康评分（health_score，0-100）
- 等级（grade）
- 事件统计（总数、错误数、警告数、错误率）
- 任务统计（总数、成功率）
- Agent 统计（总数、平均评分）

**评分算法：**
```
健康评分 = 任务成功率 * 40% + Agent 平均评分 * 40% + (1 - 错误率) * 20%
```

**示例输出：**
```json
{
  "health_score": 87.32,
  "grade": "A",
  "time_window_hours": 24,
  "events": {
    "total": 100,
    "error": 5,
    "warning": 10,
    "error_rate": 0.05
  },
  "tasks": {
    "total": 10,
    "success": 8,
    "failed": 2,
    "success_rate": 0.8
  },
  "agents": {
    "total": 3,
    "avg_score": 85.0
  }
}
```

### 4. 改进评估（evaluate_improvement）

**评估指标：**
- 改进前统计（任务数、成功率、平均耗时）
- 改进后统计（任务数、成功率、平均耗时）
- 改进幅度（成功率提升、耗时降低、综合评分）

**评分算法：**
```
综合改进评分 = 成功率提升 * 60% + 耗时降低 * 40%
```

**示例输出：**
```json
{
  "agent_id": "coder",
  "status": "ok",
  "before": {
    "tasks": 10,
    "success_rate": 0.7,
    "avg_duration_ms": 8000
  },
  "after": {
    "tasks": 10,
    "success_rate": 0.85,
    "avg_duration_ms": 5500
  },
  "improvement": {
    "success_rate_delta": 15.0,
    "duration_delta_pct": 31.25,
    "overall_score": 21.5
  }
}
```

---

## CLI 使用

### 评估任务

```bash
python evaluator.py tasks --time-window 24
python evaluator.py tasks --time-window 24 --task-type code
```

### 评估 Agent

```bash
python evaluator.py agent --agent-id coder
python evaluator.py agents
```

### 评估系统

```bash
python evaluator.py system --time-window 24
```

### 评估改进

```bash
python evaluator.py improvement --agent-id coder
```

### 生成报告

```bash
python evaluator.py report --time-window 24
```

---

## 集成示例

### 集成到 Heartbeat

```python
from aios.data_collector.evaluator import Evaluator

def heartbeat():
    evaluator = Evaluator()
    
    # 评估系统健康度
    system_eval = evaluator.evaluate_system(time_window_hours=24)
    
    # 如果健康度低于 60，发出警告
    if system_eval["health_score"] < 60:
        print(f"⚠️  系统健康度低: {system_eval['health_score']:.2f}/100")
        # 触发告警
    
    # 每天生成一次报告
    if should_generate_daily_report():
        report = evaluator.generate_report(time_window_hours=24)
        print(f"📄 每日报告已生成: {report['timestamp']}")
```

### 集成到 Self-Improving Loop

```python
from aios.data_collector.evaluator import Evaluator

def apply_improvement(agent_id: str):
    evaluator = Evaluator()
    
    # 评估改进前的性能
    before_eval = evaluator.evaluate_agent(agent_id)
    
    # 应用改进
    apply_changes(agent_id)
    
    # 等待一段时间收集数据
    time.sleep(3600)  # 1 小时
    
    # 评估改进后的性能
    improvement_eval = evaluator.evaluate_improvement(agent_id)
    
    # 如果改进效果不佳，回滚
    if improvement_eval["improvement"]["overall_score"] < 0:
        print(f"⚠️  改进效果不佳，回滚")
        rollback_changes(agent_id)
    else:
        print(f"✅ 改进成功: {improvement_eval['improvement']['overall_score']:.2f}%")
```

### 集成到 Dashboard

```python
from aios.data_collector.evaluator import Evaluator

def get_dashboard_data():
    evaluator = Evaluator()
    
    # 获取系统评估
    system_eval = evaluator.evaluate_system(time_window_hours=24)
    
    # 获取所有 Agent 评估
    agents_eval = evaluator.evaluate_all_agents()
    
    return {
        "system": system_eval,
        "agents": agents_eval
    }
```

---

## 报告格式

### 完整报告结构

```json
{
  "timestamp": "2026-02-26T15:56:29.552239Z",
  "time_window_hours": 24,
  "system": {
    "health_score": 87.32,
    "grade": "A",
    "events": {...},
    "tasks": {...},
    "agents": {...}
  },
  "tasks": {
    "total": 10,
    "success": 8,
    "failed": 2,
    "success_rate": 0.8,
    "avg_duration_ms": 5500.0,
    "avg_cost_usd": 0.05
  },
  "agents": [
    {
      "agent_id": "coder",
      "status": "idle",
      "stats": {...},
      "success_rate": 0.8,
      "avg_duration_ms": 5500,
      "total_cost_usd": 0.05,
      "score": 84.97,
      "grade": "A"
    }
  ]
}
```

---

## 常见问题

### Q: 评分算法是否可以自定义？

A: 可以。修改 `evaluate_agent()` 和 `evaluate_system()` 中的权重即可。

### Q: 如何设置评估阈值？

A: 在 `_get_grade()` 方法中修改等级划分。

### Q: 改进评估需要多长时间？

A: 默认对比最近 24 小时和之前 24 小时的数据。可以通过 `before_window_hours` 和 `after_window_hours` 参数调整。

### Q: 报告保存在哪里？

A: 默认保存在 `aios/data_collector/data/evaluations/report_*.json`。

---

## 下一步

- [ ] 集成到 AIOS Heartbeat
- [ ] 集成到 Dashboard（实时显示评分）
- [ ] 集成到 Self-Improving Loop（自动回滚）
- [ ] 增加更多评估维度（资源使用、并发性能）
- [ ] 支持自定义评分算法

---

**版本：** v1.0.0  
**最后更新：** 2026-02-26  
**维护者：** 小九 + 珊瑚海
