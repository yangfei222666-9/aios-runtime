"""
统一 Schema - 支持 Skills/Agents/Coder 代码
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


class EntryType(Enum):
    """注册表条目类型"""
    SKILL = "skill"
    AGENT = "agent"
    CODER_CODE = "coder_code"


@dataclass
class RegistryEntry:
    """统一注册表条目"""
    
    # 核心字段
    name: str
    type: EntryType
    description: str
    entry_point: str  # 执行入口（文件路径或命令）
    
    # 元数据
    metadata: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # 自动生成字段
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used: Optional[str] = None
    use_count: int = 0
    
    # 可选字段
    version: str = "1.0.0"
    author: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "entry_point": self.entry_point,
            "metadata": self.metadata,
            "tags": self.tags,
            "registered_at": self.registered_at,
            "last_used": self.last_used,
            "use_count": self.use_count,
            "version": self.version,
            "author": self.author,
            "dependencies": self.dependencies,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RegistryEntry':
        """从字典创建"""
        data = data.copy()
        data['type'] = EntryType(data['type'])
        return cls(**data)
