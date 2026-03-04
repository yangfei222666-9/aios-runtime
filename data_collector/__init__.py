"""
AIOS Data Collector - 统一数据采集层

核心功能：
1. 统一入口 - 所有数据采集走一个接口
2. 标准 Schema - 5 种核心数据类型（Event/Task/Agent/Trace/Metric）
3. 自动关联 - task/agent/trace 自动串联
4. 智能归档 - 按日期/类型分类，自动清理
5. 高性能 - 异步写入，批量提交

使用示例：
    from aios.data_collector import DataCollector
    
    collector = DataCollector()
    
    # 记录事件
    collector.log_event(
        type="task_started",
        severity="info",
        task_id="task_xxx",
        agent_id="coder"
    )
    
    # 创建任务
    task_id = collector.create_task(
        title="实现功能",
        type="code",
        priority="high"
    )
    
    # 查询
    events = collector.query_events(task_id="task_xxx")
"""

from .collector import DataCollector
from .schema import Event, Task, Agent, Trace, Metric

__all__ = ["DataCollector", "Event", "Task", "Agent", "Trace", "Metric"]
__version__ = "1.0.0"
