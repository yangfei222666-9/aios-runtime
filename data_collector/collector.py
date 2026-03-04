"""
核心采集器 - 统一数据采集入口
"""

from typing import Optional, Dict, Any, List
from .schema import Event, Task, Agent, Trace, Metric, Span, now_iso
from .storage import Storage
import os


class DataCollector:
    """数据采集器（全局单例）"""
    
    _instance = None
    _instances = {}  # 支持多个实例（用于测试）
    
    def __new__(cls, base_dir: Optional[str] = None):
        # 如果指定了 base_dir，创建独立实例（用于测试）
        if base_dir is not None:
            instance = super().__new__(cls)
            instance._initialized = False
            return instance
        
        # 否则使用全局单例
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, base_dir: Optional[str] = None):
        if self._initialized:
            return
        
        if base_dir is None:
            # 默认路径：aios/data/
            base_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data"
            )
        
        self.storage = Storage(base_dir)
        self._initialized = True
    
    # ==================== Event ====================
    
    def log_event(
        self,
        type: str,
        severity: str = "info",
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> str:
        """记录事件
        
        Args:
            type: 事件类型
            severity: 严重程度（debug|info|warning|error|critical）
            task_id: 关联任务 ID
            agent_id: 关联 Agent ID
            trace_id: 关联追踪 ID
            span_id: 关联 Span ID
            payload: 额外数据
        
        Returns:
            事件 ID
        """
        event = Event(
            type=type,
            severity=severity,
            task_id=task_id,
            agent_id=agent_id,
            trace_id=trace_id,
            span_id=span_id,
            payload=payload or {}
        )
        
        self.storage.append("events", event.to_dict(), use_date=True)
        return event.id
    
    def query_events(
        self,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """查询事件
        
        Args:
            task_id: 任务 ID
            agent_id: Agent ID
            trace_id: 追踪 ID
            type: 事件类型
            severity: 严重程度
            limit: 最大返回数量
        
        Returns:
            事件列表
        """
        filters = {}
        if task_id:
            filters["task_id"] = task_id
        if agent_id:
            filters["agent_id"] = agent_id
        if trace_id:
            filters["trace_id"] = trace_id
        if type:
            filters["type"] = type
        if severity:
            filters["severity"] = severity
        
        return self.storage.query("events", filters, limit)
    
    # ==================== Task ====================
    
    def create_task(
        self,
        title: str,
        type: str,
        priority: str = "normal",
        agent_id: Optional[str] = None,
        parent_task_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> str:
        """创建任务
        
        Args:
            title: 任务标题
            type: 任务类型（code|analysis|monitor|research|design）
            priority: 优先级（high|normal|low）
            agent_id: 分配的 Agent ID
            parent_task_id: 父任务 ID
            trace_id: 追踪 ID
        
        Returns:
            任务 ID
        """
        task = Task(
            title=title,
            type=type,
            priority=priority,
            agent_id=agent_id,
            parent_task_id=parent_task_id,
            trace_id=trace_id
        )
        
        self.storage.append("tasks", task.to_dict(), use_date=False)
        
        # 记录事件
        self.log_event(
            type="task_created",
            severity="info",
            task_id=task.id,
            agent_id=agent_id,
            trace_id=trace_id,
            payload={"title": title, "type": type, "priority": priority}
        )
        
        return task.id
    
    def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        agent_id: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ):
        """更新任务
        
        Args:
            task_id: 任务 ID
            status: 状态（pending|running|success|failed|cancelled）
            agent_id: Agent ID
            result: 执行结果
            metrics: 性能指标
        """
        updates = {}
        
        if status:
            updates["status"] = status
            if status == "running" and "started_at" not in updates:
                updates["started_at"] = now_iso()
            elif status in ["success", "failed", "cancelled"] and "completed_at" not in updates:
                updates["completed_at"] = now_iso()
        
        if agent_id:
            updates["agent_id"] = agent_id
        
        if result:
            updates["result"] = result
        
        if metrics:
            updates["metrics"] = metrics
        
        self.storage.update("tasks", "id", task_id, updates)
        
        # 记录事件
        if status:
            self.log_event(
                type=f"task_{status}",
                severity="info" if status == "success" else "warning",
                task_id=task_id,
                agent_id=agent_id,
                payload=updates
            )
    
    def complete_task(
        self,
        task_id: str,
        status: str = "success",
        result: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ):
        """完成任务
        
        Args:
            task_id: 任务 ID
            status: 状态（success|failed）
            result: 执行结果
            metrics: 性能指标
        """
        self.update_task(
            task_id=task_id,
            status=status,
            result=result,
            metrics=metrics
        )
    
    def query_tasks(
        self,
        status: Optional[str] = None,
        type: Optional[str] = None,
        agent_id: Optional[str] = None,
        priority: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """查询任务
        
        Args:
            status: 状态
            type: 类型
            agent_id: Agent ID
            priority: 优先级
            limit: 最大返回数量
        
        Returns:
            任务列表
        """
        filters = {}
        if status:
            filters["status"] = status
        if type:
            filters["type"] = type
        if agent_id:
            filters["agent_id"] = agent_id
        if priority:
            filters["priority"] = priority
        
        return self.storage.query("tasks", filters, limit)
    
    # ==================== Agent ====================
    
    def update_agent(
        self,
        agent_id: str,
        type: Optional[str] = None,
        status: Optional[str] = None,
        stats: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """更新 Agent 状态
        
        Args:
            agent_id: Agent ID
            type: Agent 类型
            status: 状态（idle|busy|failed|disabled）
            stats: 统计数据
            config: 配置
        """
        updates = {"last_active": now_iso()}
        
        if type:
            updates["type"] = type
        
        if status:
            updates["status"] = status
        
        if stats:
            updates["stats"] = stats
        
        if config:
            updates["config"] = config
        
        self.storage.update("agents", "id", agent_id, updates)
        
        # 记录事件
        self.log_event(
            type="agent_updated",
            severity="info",
            agent_id=agent_id,
            payload=updates
        )
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取 Agent 状态
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Agent 数据（如果不存在返回 None）
        """
        results = self.storage.query("agents", {"id": agent_id}, limit=1)
        return results[0] if results else None
    
    # ==================== Trace ====================
    
    def create_trace(self, task_id: Optional[str] = None) -> str:
        """创建追踪链路
        
        Args:
            task_id: 关联任务 ID
        
        Returns:
            追踪 ID
        """
        trace = Trace(task_id=task_id)
        self.storage.append("traces", trace.to_dict(), use_date=True)
        return trace.trace_id
    
    def add_span(
        self,
        trace_id: str,
        name: str,
        tags: Optional[Dict[str, Any]] = None
    ) -> str:
        """添加 Span
        
        Args:
            trace_id: 追踪 ID
            name: Span 名称
            tags: 标签
        
        Returns:
            Span ID
        """
        span = Span(name=name, tags=tags or {})
        
        # 这里简化处理，实际应该更新 Trace 对象
        # 暂时只记录事件
        self.log_event(
            type="span_created",
            severity="debug",
            trace_id=trace_id,
            span_id=span.span_id,
            payload={"name": name, "tags": tags}
        )
        
        return span.span_id
    
    # ==================== Metric ====================
    
    def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, Any]] = None
    ):
        """记录指标
        
        Args:
            name: 指标名称
            value: 指标值
            tags: 标签
        """
        metric = Metric(name=name, value=value, tags=tags or {})
        self.storage.append("metrics", metric.to_dict(), use_date=True)
