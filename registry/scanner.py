"""
自动扫描器 - 扫描 skills/ 和 agents/ 目录
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from .schema import RegistryEntry, EntryType


class Scanner:
    """自动扫描器"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.skills_dir = self.workspace_root / "skills"
        self.agents_dir = self.workspace_root / "aios" / "agents"
    
    def scan_all(self) -> List[RegistryEntry]:
        """扫描所有 Skills 和 Agents"""
        entries = []
        entries.extend(self.scan_skills())
        entries.extend(self.scan_agents())
        return entries
    
    def scan_skills(self) -> List[RegistryEntry]:
        """扫描 Skills 目录"""
        entries = []
        
        if not self.skills_dir.exists():
            return entries
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            
            # 解析 SKILL.md
            entry = self._parse_skill_md(skill_dir, skill_md)
            if entry:
                entries.append(entry)
        
        return entries
    
    def scan_agents(self) -> List[RegistryEntry]:
        """扫描 Agents 目录"""
        entries = []
        
        if not self.agents_dir.exists():
            return entries
        
        for agent_dir in self.agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            
            # 查找 agent 配置文件
            config_file = agent_dir / "config.json"
            if config_file.exists():
                entry = self._parse_agent_config(agent_dir, config_file)
                if entry:
                    entries.append(entry)
            else:
                # 查找 Python 文件
                py_files = list(agent_dir.glob("*.py"))
                if py_files:
                    entry = self._parse_agent_py(agent_dir, py_files[0])
                    if entry:
                        entries.append(entry)
        
        return entries
    
    def _parse_skill_md(self, skill_dir: Path, skill_md: Path) -> Optional[RegistryEntry]:
        """解析 SKILL.md"""
        try:
            content = skill_md.read_text(encoding='utf-8')
            
            # 提取 frontmatter
            metadata = self._extract_frontmatter(content)
            
            # 查找入口脚本
            entry_point = self._find_entry_point(skill_dir)
            
            return RegistryEntry(
                name=metadata.get('name', skill_dir.name),
                type=EntryType.SKILL,
                description=metadata.get('description', ''),
                entry_point=str(entry_point) if entry_point else str(skill_dir),
                metadata=metadata,
                tags=metadata.get('tags', []),
                version=metadata.get('version', '1.0.0'),
                author=metadata.get('author'),
            )
        except Exception as e:
            print(f"Error parsing {skill_md}: {e}")
            return None
    
    def _parse_agent_config(self, agent_dir: Path, config_file: Path) -> Optional[RegistryEntry]:
        """解析 Agent 配置文件"""
        try:
            config = json.loads(config_file.read_text(encoding='utf-8'))
            
            return RegistryEntry(
                name=config.get('name', agent_dir.name),
                type=EntryType.AGENT,
                description=config.get('description', ''),
                entry_point=str(agent_dir / config.get('entry_point', 'agent.py')),
                metadata=config,
                tags=config.get('tags', []),
                version=config.get('version', '1.0.0'),
                author=config.get('author'),
            )
        except Exception as e:
            print(f"Error parsing {config_file}: {e}")
            return None
    
    def _parse_agent_py(self, agent_dir: Path, py_file: Path) -> Optional[RegistryEntry]:
        """解析 Agent Python 文件"""
        try:
            # 简单解析：从文件名和目录名推断
            return RegistryEntry(
                name=agent_dir.name,
                type=EntryType.AGENT,
                description=f"Agent: {agent_dir.name}",
                entry_point=str(py_file),
                metadata={'source': 'auto_detected'},
                tags=['agent'],
            )
        except Exception as e:
            print(f"Error parsing {py_file}: {e}")
            return None
    
    def _extract_frontmatter(self, content: str) -> Dict:
        """提取 SKILL.md 的 frontmatter"""
        metadata = {}
        
        # 简单解析：查找 --- 包围的 YAML 块
        if content.startswith('---'):
            lines = content.split('\n')
            in_frontmatter = False
            frontmatter_lines = []
            
            for line in lines[1:]:
                if line.strip() == '---':
                    break
                frontmatter_lines.append(line)
            
            # 简单解析 key: value
            for line in frontmatter_lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
        
        return metadata
    
    def _find_entry_point(self, skill_dir: Path) -> Optional[Path]:
        """查找 Skill 的入口脚本"""
        # 优先级：skill.py > main.py > *.py
        candidates = [
            skill_dir / "skill.py",
            skill_dir / "main.py",
            skill_dir / f"{skill_dir.name}.py",
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        # 查找任意 .py 文件
        py_files = list(skill_dir.glob("*.py"))
        if py_files:
            return py_files[0]
        
        return None
