"""
DataCollector 测试
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path

# 添加 aios 到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_collector import DataCollector


def setup_test_env():
    """设置测试环境"""
    test_dir = tempfile.mkdtemp(prefix="aios_test_")
    return test_dir


def cleanup_test_env(test_dir):
    """清理测试环境"""
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_event_logging():
    """测试事件记录"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    
    # 记录事件
    event_id = collector.log_event(
        type="test_event",
        severity="info",
        task_id="task_123",
        agent_id="coder",
        payload={"key": "value"}
    )
    
    assert event_id.startswith("evt_"), f"Event ID 格式错误: {event_id}"
    
    # 查询事件
    events = collector.query_events(task_id="task_123")
    assert len(events) == 1, f"应该有 1 个事件，实际: {len(events)}"
    assert events[0]["type"] == "test_event"
    assert events[0]["agent_id"] == "coder"
    
    cleanup_test_env(test_dir)
    print("✅ test_event_logging")


def test_task_lifecycle():
    """测试任务生命周期"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    
    # 创建任务
    task_id = collector.create_task(
        title="测试任务",
        type="code",
        priority="high"
    )
    
    assert task_id.startswith("task_"), f"Task ID 格式错误: {task_id}"
    
    # 更新任务状态
    collector.update_task(task_id, status="running")
    
    # 完成任务
    collector.complete_task(
        task_id,
        status="success",
        result={"output": "done"},
        metrics={"duration_ms": 1000}
    )
    
    # 查询任务
    tasks = collector.query_tasks(status="success")
    assert len(tasks) == 1, f"应该有 1 个成功任务，实际: {len(tasks)}"
    assert tasks[0]["title"] == "测试任务"
    assert tasks[0]["metrics"]["duration_ms"] == 1000
    
    cleanup_test_env(test_dir)
    print("✅ test_task_lifecycle")


def test_agent_update():
    """测试 Agent 状态更新"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    
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
    assert agent is not None, "Agent 不应该为 None"
    assert agent["status"] == "busy"
    assert agent["stats"]["tasks_total"] == 10
    
    cleanup_test_env(test_dir)
    print("✅ test_agent_update")


def test_trace_creation():
    """测试追踪链路创建"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    
    # 创建追踪
    trace_id = collector.create_trace(task_id="task_123")
    assert trace_id.startswith("trace_"), f"Trace ID 格式错误: {trace_id}"
    
    # 添加 Span
    span_id = collector.add_span(
        trace_id=trace_id,
        name="code_generation",
        tags={"model": "claude-sonnet-4-6"}
    )
    assert span_id.startswith("span_"), f"Span ID 格式错误: {span_id}"
    
    cleanup_test_env(test_dir)
    print("✅ test_trace_creation")


def test_metric_recording():
    """测试指标记录"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    
    # 记录指标
    collector.record_metric(
        name="task_duration_ms",
        value=1500.0,
        tags={"task_type": "code", "status": "success"}
    )
    
    # 读取指标（通过 storage）
    metrics = collector.storage.read_all("metrics")
    assert len(metrics) >= 1, f"应该至少有 1 个指标，实际: {len(metrics)}"
    
    cleanup_test_env(test_dir)
    print("✅ test_metric_recording")


def test_query_filters():
    """测试查询过滤"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    
    # 创建多个任务
    collector.create_task(title="任务1", type="code", priority="high")
    collector.create_task(title="任务2", type="analysis", priority="normal")
    collector.create_task(title="任务3", type="code", priority="low")
    
    # 查询 code 类型任务
    code_tasks = collector.query_tasks(type="code")
    assert len(code_tasks) == 2, f"应该有 2 个 code 任务，实际: {len(code_tasks)}"
    
    # 查询 high 优先级任务
    high_tasks = collector.query_tasks(priority="high")
    assert len(high_tasks) == 1, f"应该有 1 个 high 任务，实际: {len(high_tasks)}"
    
    cleanup_test_env(test_dir)
    print("✅ test_query_filters")


def test_event_severity_levels():
    """测试事件严重程度"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    
    # 记录不同严重程度的事件
    collector.log_event(type="debug_event", severity="debug")
    collector.log_event(type="info_event", severity="info")
    collector.log_event(type="warning_event", severity="warning")
    collector.log_event(type="error_event", severity="error")
    collector.log_event(type="critical_event", severity="critical")
    
    # 查询 error 级别事件
    error_events = collector.query_events(severity="error")
    assert len(error_events) == 1, f"应该有 1 个 error 事件，实际: {len(error_events)}"
    
    # 查询 critical 级别事件
    critical_events = collector.query_events(severity="critical")
    assert len(critical_events) == 1, f"应该有 1 个 critical 事件，实际: {len(critical_events)}"
    
    cleanup_test_env(test_dir)
    print("✅ test_event_severity_levels")


def test_task_parent_child():
    """测试父子任务关系"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    
    # 创建父任务
    parent_id = collector.create_task(
        title="父任务",
        type="code",
        priority="high"
    )
    
    # 创建子任务
    child_id = collector.create_task(
        title="子任务",
        type="code",
        priority="normal",
        parent_task_id=parent_id
    )
    
    # 查询所有任务
    all_tasks = collector.query_tasks()
    assert len(all_tasks) == 2, f"应该有 2 个任务，实际: {len(all_tasks)}"
    
    # 验证子任务的 parent_task_id
    child_task = [t for t in all_tasks if t["id"] == child_id][0]
    assert child_task["parent_task_id"] == parent_id
    
    cleanup_test_env(test_dir)
    print("✅ test_task_parent_child")


def test_agent_stats_update():
    """测试 Agent 统计更新"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    
    # 初始化 Agent
    collector.update_agent(
        agent_id="coder",
        type="coder",
        status="idle",
        stats={
            "tasks_total": 0,
            "tasks_success": 0,
            "tasks_failed": 0
        }
    )
    
    # 更新统计
    collector.update_agent(
        agent_id="coder",
        stats={
            "tasks_total": 5,
            "tasks_success": 4,
            "tasks_failed": 1
        }
    )
    
    # 验证
    agent = collector.get_agent("coder")
    assert agent["stats"]["tasks_total"] == 5
    assert agent["stats"]["tasks_success"] == 4
    
    cleanup_test_env(test_dir)
    print("✅ test_agent_stats_update")


def test_multiple_events_same_task():
    """测试同一任务的多个事件"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    
    task_id = "task_123"
    
    # 记录多个事件
    collector.log_event(type="task_started", task_id=task_id)
    collector.log_event(type="task_processing", task_id=task_id)
    collector.log_event(type="task_completed", task_id=task_id)
    
    # 查询该任务的所有事件
    events = collector.query_events(task_id=task_id)
    assert len(events) == 3, f"应该有 3 个事件，实际: {len(events)}"
    
    cleanup_test_env(test_dir)
    print("✅ test_multiple_events_same_task")


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始测试 DataCollector...\n")
    
    tests = [
        test_event_logging,
        test_task_lifecycle,
        test_agent_update,
        test_trace_creation,
        test_metric_recording,
        test_query_filters,
        test_event_severity_levels,
        test_task_parent_child,
        test_agent_stats_update,
        test_multiple_events_same_task
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test.__name__}: {e}")
            failed += 1
    
    print(f"\n📊 测试结果: {passed}/{len(tests)} 通过")
    
    if failed == 0:
        print("🎉 所有测试通过！")
    else:
        print(f"⚠️  {failed} 个测试失败")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
