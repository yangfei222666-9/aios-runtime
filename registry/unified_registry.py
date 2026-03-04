"""
统一注册表 - 核心实现
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from .schema import RegistryEntry, EntryType
from .scanner import Scanner


class UnifiedRegistry:
    """统一注册表"""
    
    def __init__(self, workspace_root: str, registry_file: Optional[str] = None):
        self.workspace_root = Path(workspace_root)
        self.registry_file = Path(registry_file) if registry_file else self.workspace_root / "aios" / "registry" / "registry.json"
        self.entries: Dict[str, RegistryEntry] = {}
        self.scanner = Scanner(workspace_root)
        
        # 加载现有注册表
        self.load()
    
    def load(self):
        """加载注册表"""
        if self.registry_file.exists():
            try:
                data = json.loads(self.registry_file.read_text(encoding='utf-8'))
                self.entries = {
                    name: RegistryEntry.from_dict(entry_data)
                    for name, entry_data in data.items()
                }
            except Exception as e:
                print(f"Error loading registry: {e}")
                self.entries = {}
    
    def save(self):
        """保存注册表"""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            name: entry.to_dict()
            for name, entry in self.entries.items()
        }
        self.registry_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def register(self, entry: RegistryEntry) -> bool:
        """注册条目"""
        if entry.name in self.entries:
            print(f"Entry {entry.name} already exists")
            return False
        
        self.entries[entry.name] = entry
        self.save()
        return True
    
    def unregister(self, name: str) -> bool:
        """注销条目"""
        if name not in self.entries:
            print(f"Entry {name} not found")
            return False
        
        del self.entries[name]
        self.save()
        return True
    
    def get(self, name: str) -> Optional[RegistryEntry]:
        """获取条目"""
        return self.entries.get(name)
    
    def list_all(self) -> List[RegistryEntry]:
        """列出所有条目"""
        return list(self.entries.values())
    
    def list_by_type(self, entry_type: EntryType) -> List[RegistryEntry]:
        """按类型列出"""
        return [entry for entry in self.entries.values() if entry.type == entry_type]
    
    def search(self, query: str) -> List[RegistryEntry]:
        """搜索条目（名称/描述/标签）"""
        query = query.lower()
        results = []
        
        for entry in self.entries.values():
            if (query in entry.name.lower() or
                query in entry.description.lower() or
                any(query in tag.lower() for tag in entry.tags)):
                results.append(entry)
        
        return results
    
    def search_by_tags(self, tags: List[str]) -> List[RegistryEntry]:
        """按标签搜索"""
        tags = [tag.lower() for tag in tags]
        results = []
        
        for entry in self.entries.values():
            entry_tags = [tag.lower() for tag in entry.tags]
            if any(tag in entry_tags for tag in tags):
                results.append(entry)
        
        return results
    
    def update_usage(self, name: str):
        """更新使用统计"""
        if name in self.entries:
            entry = self.entries[name]
            entry.use_count += 1
            entry.last_used = datetime.now().isoformat()
            self.save()
    
    def auto_scan(self) -> int:
        """自动扫描并注册新条目"""
        new_entries = self.scanner.scan_all()
        count = 0
        
        for entry in new_entries:
            if entry.name not in self.entries:
                self.entries[entry.name] = entry
                count += 1
        
        if count > 0:
            self.save()
        
        return count
    
    def stats(self) -> Dict:
        """统计信息"""
        total = len(self.entries)
        by_type = {}
        
        for entry_type in EntryType:
            by_type[entry_type.value] = len(self.list_by_type(entry_type))
        
        return {
            "total": total,
            "by_type": by_type,
            "registry_file": str(self.registry_file),
        }
