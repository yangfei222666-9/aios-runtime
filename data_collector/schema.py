"""
数据模型定义 - 5 种核心数据类型
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


def generate_id(prefix: str) -> str:
    """生成唯一 ID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def now_iso() -> str:
    """当前时间（ISO 8601 格式）"""
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class Event:
    """事件 - 系统中发生的所有事情"""
    id: str = field(default_factory=lambda: generate_id("evt"))
    ts: str = field(default_factory=now_iso)
    type: str = ""  # task_started|agent_spawned|error_occurred|...
    severity: str = "info"  # debug|info|warning|error|critical
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Task:
    """任务 - 用户请求或系统任务"""
    id: str = field(default_factory=lambda: generate_id("task"))
    title: str = ""
    type: str = ""  # code|analysis|monitor|research|design
    status: str = "pending"  # pending|running|success|failed|cancelled
    priority: str = "normal"  # high|normal|low
    created_at: str = field(default_factory=now_iso)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    agent_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    trace_id: Optional[str] = None
    result: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Agent:
    """Agent 状态"""
    id: str = ""
    type: str = ""  # coder|analyst|monitor|...
    status: str = "idle"  # idle|busy|failed|disabled
    created_at: str = field(default_factory=now_iso)
    last_active: str = field(default_factory=now_iso)
    stats: Dict[str, Any] = field(default_factory=lambda: {
        "tasks_total": 0,
        "tasks_success": 0,
        "tasks_failed": 0,
        "avg_duration_ms": 0,
        "total_cost_usd": 0.0
    })
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Span:
    """Span - 追踪链路中的一段"""
    span_id: str = field(default_factory=lambda: generate_id("span"))
    name: str = ""
    started_at: str = field(default_factory=now_iso)
    completed_at: Optional[str] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Trace:
    """追踪链路"""
    trace_id: str = field(default_factory=lambda: generate_id("trace"))
    task_id: Optional[str] = None
    started_at: str = field(default_factory=now_iso)
    completed_at: Optional[str] = None
    spans: List[Span] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["spans"] = [span.to_dict() if isinstance(span, Span) else span for span in self.spans]
        return data


@dataclass
class Metric:
    """指标 - 系统性能指标"""
    ts: str = field(default_factory=now_iso)
    name: str = ""
    value: float = 0.0
    tags: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
