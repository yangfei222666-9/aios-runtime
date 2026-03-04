#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIOS v1.1 完整打包脚本（包含 Perplexity 集成）
创建 AIOS-v1.1-full.zip
"""
import sys
import os
import zipfile
from pathlib import Path
import json
from datetime import datetime

# 设置输出编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

WORKSPACE_ROOT = Path(__file__).parent.parent
AIOS_ROOT = WORKSPACE_ROOT / "aios"
SKILLS_ROOT = WORKSPACE_ROOT / "skills"

# AIOS 核心文件
AIOS_INCLUDE = [
    "aios.py",
    "demo_simple.py",
    "demo_api_health.py",
    "README.md",
    "LICENSE",
    "observability/",
    "agent_system/",
    "dashboard/",
    "core/",
    "config.yaml",
    "API.md",
    "TUTORIAL.md",
    "AIOS_简单介绍.md",
    "AIOS_详细介绍.md",
    "PERPLEXITY_USAGE.md",
    "agents/",
    "tests/",
]

# Skills 打包（只打包 perplexity-search）
SKILLS_INCLUDE = [
    "perplexity-search/",
]

# 排除模式
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
    ".coverage",
    "htmlcov",
    "*.egg-info",
    "dist",
    "build",
    ".git",
    ".github",
    "data/",
    "logs/",
    "events.jsonl",
    "*.log",
    "node_modules/",
]

def should_include(path: Path, root: Path) -> bool:
    """判断是否应该包含该文件"""
    try:
        path_str = str(path.relative_to(root))
    except ValueError:
        return False
    
    # 检查排除模式
    for pattern in EXCLUDE_PATTERNS:
        if pattern.endswith("/"):
            if pattern[:-1] in path_str.split(os.sep):
                return False
        elif pattern.startswith("*."):
            if path.name.endswith(pattern[1:]):
                return False
        elif pattern in path_str:
            return False
    
    return True

def create_package():
    """创建完整打包文件"""
    print("=" * 70)
    print("  📦 AIOS v1.1 完整打包工具（含 Perplexity）")
    print("=" * 70)
    
    # 输出文件
    output_file = AIOS_ROOT / "AIOS-v1.1-full.zip"
    
    if output_file.exists():
        print(f"\n⚠️  删除旧文件: {output_file.name}")
        output_file.unlink()
    
    print(f"\n📝 创建打包文件: {output_file.name}")
    
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        file_count = 0
        
        # ========== 打包 AIOS 核心 ==========
        print("\n📦 打包 AIOS 核心...")
        for pattern in AIOS_INCLUDE:
            pattern_path = AIOS_ROOT / pattern
            
            if pattern.endswith("/"):
                # 目录
                dir_path = AIOS_ROOT / pattern[:-1]
                if dir_path.exists():
                    for file_path in dir_path.rglob("*"):
                        if file_path.is_file() and should_include(file_path, AIOS_ROOT):
                            arcname = f"aios/{file_path.relative_to(AIOS_ROOT)}"
                            zf.write(file_path, arcname)
                            file_count += 1
                            if file_count % 50 == 0:
                                print(f"   已打包 {file_count} 个文件...")
            else:
                # 单个文件
                if pattern_path.exists():
                    arcname = f"aios/{pattern}"
                    zf.write(pattern_path, arcname)
                    file_count += 1
        
        print(f"   ✅ AIOS 核心: {file_count} 个文件")
        
        # ========== 打包 Skills ==========
        print("\n📦 打包 Skills...")
        skills_count = 0
        for skill_pattern in SKILLS_INCLUDE:
            skill_path = SKILLS_ROOT / skill_pattern[:-1]
            if skill_path.exists():
                for file_path in skill_path.rglob("*"):
                    if file_path.is_file() and should_include(file_path, SKILLS_ROOT):
                        arcname = f"skills/{file_path.relative_to(SKILLS_ROOT)}"
                        zf.write(file_path, arcname)
                        skills_count += 1
                        file_count += 1
        
        print(f"   ✅ Skills: {skills_count} 个文件")
        
        # ========== 创建安装说明 ==========
        print("\n📝 生成安装说明...")
        install_guide = """# AIOS v1.1 安装指南

## 📦 包含内容

- **AIOS 核心系统** - 完整的 AI 操作系统
- **Perplexity Search Skill** - AI 搜索集成

## 🚀 快速开始

### 1. 解压文件

```bash
unzip AIOS-v1.1-full.zip
cd aios
```

### 2. 运行演示

```bash
python aios.py demo
```

### 3. 启动 Dashboard

```bash
python aios.py dashboard
# 访问 http://127.0.0.1:8888
```

## 🔍 Perplexity 集成

### 获取 API Key

1. 访问 https://www.perplexity.ai/settings/api
2. 注册账号（免费版可用）
3. 复制 API Key

### 设置环境变量

**Windows:**
```cmd
set PERPLEXITY_API_KEY=pplx-xxxxx
```

**Linux/Mac:**
```bash
export PERPLEXITY_API_KEY=pplx-xxxxx
```

### 测试 Perplexity

```bash
cd ../skills/perplexity-search
node test.mjs
```

### 使用 Perplexity

**方式 1：命令行**
```bash
node scripts/search.mjs "你的问题"
```

**方式 2：AIOS 任务队列**
```bash
cd ../../aios/agent_system
echo '{"id":"search_001","type":"search","message":"你的问题","priority":"normal"}' >> task_queue.jsonl
python auto_dispatcher_v2.py
```

**方式 3：语音命令**
直接说："搜索 XXX" 或 "研究 XXX"

## 📚 文档

- **AIOS 简单介绍** - `aios/AIOS_简单介绍.md`
- **AIOS 详细介绍** - `aios/AIOS_详细介绍.md`
- **Perplexity 使用指南** - `aios/PERPLEXITY_USAGE.md`
- **Perplexity Skill 文档** - `skills/perplexity-search/SKILL.md`

## 💡 系统要求

- Python 3.8+
- Node.js 18+ (仅 Perplexity Skill 需要)
- Windows / Linux / macOS

## 🆘 常见问题

### Q: Perplexity 测试失败？

A: 检查 API Key 是否设置：
```bash
echo $PERPLEXITY_API_KEY  # Linux/Mac
echo %PERPLEXITY_API_KEY%  # Windows
```

### Q: Dashboard 打不开？

A: 检查端口 8888 是否被占用：
```bash
netstat -ano | findstr :8888  # Windows
lsof -i :8888  # Linux/Mac
```

### Q: 任务不执行？

A: 查看日志：
```bash
cat aios/agent_system/dispatcher.log
```

## 📞 联系方式

- GitHub: https://github.com/yangfei222666-9/aios
- Telegram: @shh7799

---

**版本：** v1.1  
**发布日期：** 2026-02-27  
**作者：** 小九 + 珊瑚海
"""
        
        zf.writestr("INSTALL.md", install_guide)
        file_count += 1
        
        # ========== 创建版本信息 ==========
        version_info = {
            "version": "1.1.0",
            "release_date": datetime.now().isoformat(),
            "features": [
                "AIOS 核心系统",
                "Perplexity Search 集成",
                "完整可观测性",
                "自我进化闭环",
                "64 个 Agent",
                "44 个 Skill"
            ],
            "new_in_v1.1": [
                "Perplexity Search Skill",
                "Perplexity_Researcher Agent",
                "AIOS 简单介绍文档",
                "AIOS 详细介绍文档",
                "Perplexity 使用指南"
            ]
        }
        
        zf.writestr("VERSION.json", json.dumps(version_info, indent=2, ensure_ascii=False))
        file_count += 1
        
        print(f"\n✅ 打包完成！共 {file_count} 个文件")
    
    # 显示文件大小
    size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"📊 文件大小: {size_mb:.2f} MB")
    print(f"📁 输出路径: {output_file}")
    
    print("\n" + "=" * 70)
    print("  ✅ 打包成功！")
    print("=" * 70)
    
    print("\n💡 使用方法:")
    print("   1. 解压 AIOS-v1.1-full.zip")
    print("   2. 阅读 INSTALL.md")
    print("   3. cd aios && python aios.py demo")
    print("   4. 获取 Perplexity API Key 并测试")

if __name__ == "__main__":
    try:
        create_package()
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
