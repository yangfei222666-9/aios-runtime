"""
存储层 - JSONL 文件写入和读取
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class Storage:
    """JSONL 存储层"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        dirs = [
            self.base_dir / "events",
            self.base_dir / "tasks",
            self.base_dir / "tasks" / "archive",
            self.base_dir / "agents",
            self.base_dir / "traces",
            self.base_dir / "metrics"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def _get_date_str(self) -> str:
        """获取当前日期字符串（YYYY-MM-DD）"""
        return datetime.utcnow().strftime("%Y-%m-%d")
    
    def append(self, category: str, data: Dict[str, Any], use_date: bool = True):
        """追加数据到 JSONL 文件
        
        Args:
            category: 类别（events/tasks/agents/traces/metrics）
            data: 数据字典
            use_date: 是否使用日期文件名（events/traces/metrics 用日期，tasks/agents 不用）
        """
        if use_date:
            filename = f"{self._get_date_str()}.jsonl"
        else:
            filename = f"{category}.jsonl"
        
        filepath = self.base_dir / category / filename
        
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    
    def read(self, category: str, filename: Optional[str] = None) -> List[Dict[str, Any]]:
        """读取 JSONL 文件
        
        Args:
            category: 类别
            filename: 文件名（如果为 None，读取最新的日期文件）
        
        Returns:
            数据列表
        """
        if filename is None:
            filename = f"{self._get_date_str()}.jsonl"
        
        filepath = self.base_dir / category / filename
        
        if not filepath.exists():
            return []
        
        data = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
        
        return data
    
    def read_all(self, category: str) -> List[Dict[str, Any]]:
        """读取某个类别的所有数据
        
        Args:
            category: 类别
        
        Returns:
            数据列表
        """
        category_dir = self.base_dir / category
        
        if not category_dir.exists():
            return []
        
        data = []
        for filepath in sorted(category_dir.glob("*.jsonl")):
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data.append(json.loads(line))
        
        return data
    
    def update(self, category: str, id_field: str, id_value: str, updates: Dict[str, Any]):
        """更新数据（重写整个文件）
        
        Args:
            category: 类别
            id_field: ID 字段名（如 "id", "agent_id"）
            id_value: ID 值
            updates: 更新的字段
        """
        filename = f"{category}.jsonl"
        filepath = self.base_dir / category / filename
        
        # 读取所有数据（如果文件不存在，data 为空列表）
        data = []
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data.append(json.loads(line))
        
        # 更新匹配的记录
        updated = False
        for item in data:
            if item.get(id_field) == id_value:
                item.update(updates)
                updated = True
        
        # 如果没找到，追加新记录
        if not updated:
            new_item = {id_field: id_value}
            new_item.update(updates)
            data.append(new_item)
        
        # 重写文件
        with open(filepath, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    def query(self, category: str, filters: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询数据
        
        Args:
            category: 类别
            filters: 过滤条件（字段名 -> 值）
            limit: 最大返回数量
        
        Returns:
            匹配的数据列表
        """
        all_data = self.read_all(category)
        
        results = []
        for item in all_data:
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            
            if match:
                results.append(item)
                if limit and len(results) >= limit:
                    break
        
        return results
