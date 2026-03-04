#!/usr/bin/env python3
"""
Skill Registry - 扫描和管理所有 Skills
"""
import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


WORKSPACE = Path(os.getenv("OPENCLAW_WORKSPACE", Path.home() / ".openclaw" / "workspace"))
SKILLS_DIR = WORKSPACE / "skills"
REGISTRY_CACHE = WORKSPACE / "aios" / "skills" / "registry.json"


@dataclass
class SkillManifest:
    """Skill 清单"""
    name: str
    version: str
    description: str
    entrypoint: str
    
    # Schema
    inputs_schema: Optional[Dict] = None
    outputs_schema: Optional[Dict] = None
    
    # 权限
    capabilities: List[str] = None
    risk_level: str = "low"
    auto_approve: bool = True
    
    # 触发器
    triggers: List[Dict] = None
    
    # 运行时
    runtime: Optional[Dict] = None
    
    # 路由
    routing: Optional[Dict] = None
    
    # 依赖
    dependencies: List[str] = None
    
    # 环境变量
    env: Optional[Dict] = None
    
    # 元数据
    icon: Optional[str] = None
    author: Optional[str] = None
    license: Optional[str] = None
    homepage: Optional[str] = None
    
    # Agent Prompt
    default_prompt: Optional[str] = None
    
    # 内部字段
    skill_path: Optional[str] = None
    yaml_path: Optional[str] = None
    last_scanned: Optional[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.triggers is None:
            self.triggers = [{"type": "on_demand"}]
        if self.dependencies is None:
            self.dependencies = []


class SkillRegistry:
    """Skill 注册表"""
    
    def __init__(self):
        self.skills: Dict[str, SkillManifest] = {}
        self.load_cache()
    
    def scan(self, force: bool = False):
        """扫描所有 Skills"""
        if not SKILLS_DIR.exists():
            print(f"⚠️  Skills 目录不存在: {SKILLS_DIR}")
            return
        
        print(f"🔍 扫描 Skills: {SKILLS_DIR}\n")
        
        found = 0
        errors = 0
        
        for skill_dir in SKILLS_DIR.iterdir():
            if not skill_dir.is_dir():
                continue
            if skill_dir.name.startswith("."):
                continue
            
            # 查找 skill.yaml
            skill_yaml = skill_dir / "skill.yaml"
            if not skill_yaml.exists():
                continue
            
            try:
                manifest = self.load_manifest(skill_yaml, skill_dir)
                self.skills[manifest.name] = manifest
                found += 1
                print(f"✅ {manifest.name} v{manifest.version}")
            except Exception as e:
                errors += 1
                print(f"❌ {skill_dir.name}: {e}")
        
        print(f"\n📊 扫描完成: {found} 个 Skills，{errors} 个错误")
        
        # 保存缓存
        self.save_cache()
    
    def load_manifest(self, yaml_path: Path, skill_dir: Path) -> SkillManifest:
        """加载 skill.yaml"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 验证必需字段
        required = ['name', 'version', 'description', 'entrypoint']
        for field in required:
            if field not in data:
                raise ValueError(f"缺少必需字段: {field}")
        
        # 添加内部字段
        data['skill_path'] = str(skill_dir)
        data['yaml_path'] = str(yaml_path)
        data['last_scanned'] = datetime.now().isoformat()
        
        return SkillManifest(**data)
    
    def get(self, name: str) -> Optional[SkillManifest]:
        """获取 Skill"""
        return self.skills.get(name)
    
    def list(self, tags: List[str] = None, risk_level: str = None) -> List[SkillManifest]:
        """列出 Skills"""
        results = list(self.skills.values())
        
        # 按标签过滤
        if tags:
            results = [
                s for s in results
                if s.routing and any(tag in s.routing.get('tags', []) for tag in tags)
            ]
        
        # 按风险等级过滤
        if risk_level:
            results = [s for s in results if s.risk_level == risk_level]
        
        return results
    
    def save_cache(self):
        """保存缓存"""
        REGISTRY_CACHE.parent.mkdir(parents=True, exist_ok=True)
        
        cache = {
            "skills": {name: asdict(manifest) for name, manifest in self.skills.items()},
            "last_updated": datetime.now().isoformat(),
            "total": len(self.skills)
        }
        
        REGISTRY_CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def load_cache(self):
        """加载缓存"""
        if not REGISTRY_CACHE.exists():
            return
        
        try:
            cache = json.loads(REGISTRY_CACHE.read_text(encoding='utf-8'))
            for name, data in cache.get("skills", {}).items():
                self.skills[name] = SkillManifest(**data)
        except Exception as e:
            print(f"⚠️  加载缓存失败: {e}")


def format_skill_card(skill: SkillManifest) -> str:
    """格式化 Skill 卡片"""
    lines = [
        f"📦 {skill.icon or ''} {skill.name} v{skill.version}",
        f"   {skill.description}",
        f"   🔧 入口: {skill.entrypoint}",
    ]
    
    if skill.capabilities:
        lines.append(f"   🔐 能力: {', '.join(skill.capabilities)}")
    
    lines.append(f"   ⚠️  风险: {skill.risk_level}")
    lines.append(f"   ✅ 自动批准: {'是' if skill.auto_approve else '否'}")
    
    if skill.routing and skill.routing.get('tags'):
        lines.append(f"   🏷️  标签: {', '.join(skill.routing['tags'])}")
    
    if skill.author:
        lines.append(f"   👤 作者: {skill.author}")
    
    return "\n".join(lines)


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
🔍 Skill Registry - 扫描和管理 Skills

用法:
  python skill_registry.py scan [--force]
  python skill_registry.py list [--tags tag1,tag2] [--risk low|medium|high]
  python skill_registry.py show <skill-name>
  python skill_registry.py stats

命令:
  scan              扫描所有 Skills
  list              列出所有 Skills
  show <name>       显示 Skill 详情
  stats             显示统计信息

示例:
  python skill_registry.py scan
  python skill_registry.py list --tags monitoring
  python skill_registry.py show server_health_agent
        """)
        return
    
    cmd = sys.argv[1]
    registry = SkillRegistry()
    
    if cmd == "scan":
        force = "--force" in sys.argv
        registry.scan(force=force)
    
    elif cmd == "list":
        # 解析参数
        tags = None
        risk_level = None
        
        if "--tags" in sys.argv:
            idx = sys.argv.index("--tags")
            tags = sys.argv[idx + 1].split(",")
        
        if "--risk" in sys.argv:
            idx = sys.argv.index("--risk")
            risk_level = sys.argv[idx + 1]
        
        skills = registry.list(tags=tags, risk_level=risk_level)
        
        if not skills:
            print("❌ 没有找到 Skills")
            return
        
        print(f"📋 Skills ({len(skills)} 个):\n")
        for skill in sorted(skills, key=lambda s: s.name):
            print(format_skill_card(skill))
            print()
    
    elif cmd == "show":
        if len(sys.argv) < 3:
            print("❌ 请提供 Skill 名称")
            return
        
        name = sys.argv[2]
        skill = registry.get(name)
        
        if not skill:
            print(f"❌ Skill 不存在: {name}")
            return
        
        print(format_skill_card(skill))
        
        # 显示详细信息
        if skill.inputs_schema:
            print("\n📥 输入 Schema:")
            print(json.dumps(skill.inputs_schema, indent=2))
        
        if skill.outputs_schema:
            print("\n📤 输出 Schema:")
            print(json.dumps(skill.outputs_schema, indent=2))
        
        if skill.default_prompt:
            print("\n💬 默认 Prompt:")
            print(skill.default_prompt)
    
    elif cmd == "stats":
        print("📊 统计信息:\n")
        print(f"总 Skills: {len(registry.skills)}")
        
        # 按风险等级统计
        risk_counts = {}
        for skill in registry.skills.values():
            risk_counts[skill.risk_level] = risk_counts.get(skill.risk_level, 0) + 1
        
        print("\n风险等级分布:")
        for level, count in sorted(risk_counts.items()):
            print(f"  {level}: {count}")
        
        # 按能力统计
        cap_counts = {}
        for skill in registry.skills.values():
            for cap in skill.capabilities:
                cap_counts[cap] = cap_counts.get(cap, 0) + 1
        
        if cap_counts:
            print("\n能力分布:")
            for cap, count in sorted(cap_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {cap}: {count}")
    
    else:
        print(f"❌ 未知命令: {cmd}")


if __name__ == "__main__":
    main()
