#!/usr/bin/env python3
"""
AIOS 打包工具 - 朋友版
生成一个友好的、开箱即用的 AIOS 包
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_package():
    """创建 AIOS 朋友版打包"""
    
    # 1. 创建临时目录
    temp_dir = Path("AIOS-Friend-Edition")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    print(f"📦 创建打包目录: {temp_dir}")
    
    # 2. 复制核心文件
    core_files = [
        "aios.py",
        "config.yaml",
        "setup.py",
        "pyproject.toml",
        "LICENSE",
    ]
    
    for file in core_files:
        if os.path.exists(file):
            shutil.copy2(file, temp_dir / file)
            print(f"  ✅ {file}")
    
    # 3. 复制核心目录
    core_dirs = [
        "core",
        "aios",
        "agent_system",
        "storage",
        "sdk",
        "demo_data",
    ]
    
    for dir_name in core_dirs:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, temp_dir / dir_name, 
                          ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.pytest_cache'))
            print(f"  ✅ {dir_name}/")
    
    # 4. 创建中文 README
    readme_content = """# AIOS - AI 操作系统（朋友版）

## 🚀 10 秒快速开始

### Windows 用户：
1. 双击 `install.bat` 安装依赖（只需一次）
2. 双击 `run.bat` 运行演示

### Mac/Linux 用户：
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行演示
python aios.py demo --scenario 1
```

---

## 💡 AIOS 是什么？

AIOS 是一个**轻量级的 AI 操作系统**，让你的 AI Agent 能够：

- 🤖 **自主运行** — 自动调度任务，无需人工干预
- 👁️ **自我观测** — 实时监控性能、成本、错误
- 🧬 **自我进化** — 从失败中学习，自动优化策略

---

## 🎯 3 个演示场景

### 场景 1：文件监控 + 自动分类
```bash
python aios.py demo --scenario 1
```
- 监控文件变化
- 自动分类文件（按扩展名）
- 生成分类报告

### 场景 2：API 健康检查 + 自动恢复
```bash
python aios.py demo --scenario 2
```
- 检查 API 健康状态
- 自动重试失败请求
- 记录恢复过程

### 场景 3：日志分析 + 自动生成 Playbook
```bash
python aios.py demo --scenario 3
```
- 分析错误日志
- 识别高频错误
- 自动生成修复 Playbook

---

## 📊 查看 Dashboard

```bash
python aios.py dashboard
```

然后打开浏览器访问：http://127.0.0.1:9091

---

## 🎯 提交任务

```bash
# 提交一个代码任务
python aios.py submit --desc "重构 scheduler.py" --type code --priority high

# 查看任务状态
python aios.py tasks

# 运行心跳（自动执行任务）
python aios.py heartbeat
```

---

## 📚 更多文档

- GitHub: https://github.com/yangfei222666-9/AIOS
- 完整文档: 见 `docs/` 目录

---

## 🐛 遇到问题？

1. **端口被占用** - 修改 `config.yaml` 中的 `dashboard.port`
2. **依赖缺失** - 运行 `pip install -r requirements.txt`
3. **其他问题** - 查看 `logs/` 目录的日志文件

---

**版本：** v1.3  
**打包时间：** """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """  
**作者：** 珊瑚海 + 小九  
"""
    
    (temp_dir / "README.txt").write_text(readme_content, encoding="utf-8")
    print("  ✅ README.txt")
    
    # 5. 创建 run.bat
    run_bat = """@echo off
chcp 65001 >nul
echo ========================================
echo AIOS 演示启动器
echo ========================================
echo.
echo 选择演示场景:
echo   1. 文件监控 + 自动分类
echo   2. API 健康检查 + 自动恢复
echo   3. 日志分析 + 自动生成 Playbook
echo.
set /p choice="请输入场景编号 (1-3): "

if "%choice%"=="1" (
    python aios.py demo --scenario 1
) else if "%choice%"=="2" (
    python aios.py demo --scenario 2
) else if "%choice%"=="3" (
    python aios.py demo --scenario 3
) else (
    echo 无效的选择！
)

echo.
pause
"""
    (temp_dir / "run.bat").write_text(run_bat, encoding="utf-8")
    print("  ✅ run.bat")
    
    # 6. 创建 install.bat
    install_bat = """@echo off
chcp 65001 >nul
echo ========================================
echo AIOS 依赖安装器
echo ========================================
echo.
echo 正在检查 Python...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python！
    echo 请先安装 Python 3.8+
    pause
    exit /b 1
)

echo.
echo 正在安装依赖...
pip install -r requirements.txt

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步: 双击 run.bat 运行演示
echo.
pause
"""
    (temp_dir / "install.bat").write_text(install_bat, encoding="utf-8")
    print("  ✅ install.bat")
    
    # 7. 创建 requirements.txt
    requirements = """# AIOS 核心依赖（可选）
# 注意：AIOS 核心功能使用纯 Python 标准库，无需额外依赖
# 以下依赖仅用于增强功能

# 数据库（可选）
# aiosqlite>=0.17.0

# 测试（可选）
# pytest>=7.0.0
# pytest-asyncio>=0.21.0
# pytest-cov>=4.0.0
"""
    (temp_dir / "requirements.txt").write_text(requirements, encoding="utf-8")
    print("  ✅ requirements.txt")
    
    # 8. 创建 .gitignore
    gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# AIOS
aios.db
*.jsonl
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
    (temp_dir / ".gitignore").write_text(gitignore, encoding="utf-8")
    print("  ✅ .gitignore")
    
    # 9. 打包成 zip
    zip_name = f"AIOS-Friend-Edition-{datetime.now().strftime('%Y%m%d')}.zip"
    
    print(f"\n📦 正在打包: {zip_name}")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir.parent)
                zipf.write(file_path, arcname)
                print(f"  ✅ {arcname}")
    
    # 10. 清理临时目录
    shutil.rmtree(temp_dir)
    
    # 11. 获取文件大小
    size_mb = os.path.getsize(zip_name) / 1024 / 1024
    
    print(f"\n✅ 打包完成！")
    print(f"📦 文件: {zip_name}")
    print(f"📊 大小: {size_mb:.2f} MB")
    print(f"📍 路径: {os.path.abspath(zip_name)}")
    
    return zip_name

if __name__ == "__main__":
    create_package()
