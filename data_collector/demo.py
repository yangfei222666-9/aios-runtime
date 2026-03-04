"""
DataCollector 演示脚本

展示 DataCollector 的核心功能：
1. 记录事件
2. 管理任务
3. 更新 Agent 状态
4. 追踪链路
5. 记录指标
"""

import sys
from pathlib import Path

# 添加 aios 到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_collector import DataCollector


def demo():
    """演示 DataCollector 功能"""
    print("🚀 DataCollector 演示\n")
    
    # 初始化
    collector = DataCollector()
    print("✅ DataCollector 初始化完成\n")
    
    # 1. 创建任务
    print("📋 创建任务...")
    task_id = collector.create_task(
        title="实现 DataCollector",
        type="code",
        priority="high",
        agent_id="coder"
    )
    print(f"   任务 ID: {task_id}\n")
    
    # 2. 记录事件
    print("📝 记录事件...")
    collector.log_event(
        type="task_started",
        severity="info",
        task_id=task_id,
        agent_id="coder",
        payload={"model": "claude-sonnet-4-6"}
    )
    print("   事件已记录\n")
    
    # 3. 更新任务状态
    print("🔄 更新任务状态...")
    collector.update_task(task_id, status="running")
    print("   任务状态: running\n")
    
    # 4. 更新 Agent 状态
    print("🤖 更新 Agent 状态...")
    collector.update_agent(
        agent_id="coder",
        type="coder",
        status="busy",
        stats={
            "tasks_total": 1,
            "tasks_success": 0,
            "tasks_failed": 0
        }
    )
    print("   Agent 状态: busy\n")
    
    # 5. 创建追踪
    print("🔍 创建追踪链路...")
    trace_id = collector.create_trace(task_id=task_id)
    print(f"   追踪 ID: {trace_id}\n")
    
    # 6. 添加 Span
    print("📊 添加 Span...")
    span_id = collector.add_span(
        trace_id=trace_id,
        name="code_generation",
        tags={"model": "claude-sonnet-4-6"}
    )
    print(f"   Span ID: {span_id}\n")
    
    # 7. 记录指标
    print("📈 记录指标...")
    collector.record_metric(
        name="task_duration_ms",
        value=5000.0,
        tags={"task_type": "code", "status": "running"}
    )
    print("   指标已记录\n")
    
    # 8. 完成任务
    print("✅ 完成任务...")
    collector.complete_task(
        task_id,
        status="success",
        result={"code": "DataCollector 实现完成"},
        metrics={"duration_ms": 5000, "tokens_used": 1000}
    )
    print("   任务状态: success\n")
    
    # 9. 查询数据
    print("🔎 查询数据...\n")
    
    # 查询事件
    events = collector.query_events(task_id=task_id)
    print(f"   事件数量: {len(events)}")
    for event in events:
        print(f"     - {event['type']} ({event['severity']})")
    print()
    
    # 查询任务
    tasks = collector.query_tasks(status="success")
    print(f"   成功任务数量: {len(tasks)}")
    for task in tasks:
        print(f"     - {task['title']} ({task['type']})")
    print()
    
    # 查询 Agent
    agent = collector.get_agent("coder")
    if agent:
        print(f"   Agent: {agent['id']}")
        print(f"     状态: {agent['status']}")
        print(f"     统计: {agent['stats']}")
    print()
    
    print("🎉 演示完成！")
    print("\n📂 数据已保存到: aios/data/")
    print("   - events/2026-02-26.jsonl")
    print("   - tasks/tasks.jsonl")
    print("   - agents/agents.jsonl")
    print("   - traces/2026-02-26.jsonl")
    print("   - metrics/2026-02-26.jsonl")


if __name__ == "__main__":
    demo()
