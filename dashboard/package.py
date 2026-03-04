"""
AIOS Dashboard 打包脚本
生成独立可运行的 Dashboard 包
"""
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

VERSION = "v3.4"
PACKAGE_NAME = f"AIOS-Dashboard-{VERSION}"

# 源目录
DASHBOARD_DIR = Path(__file__).parent
AIOS_ROOT = DASHBOARD_DIR.parent

# 打包目录
PACKAGE_DIR = DASHBOARD_DIR / PACKAGE_NAME
PACKAGE_DIR.mkdir(exist_ok=True)

print(f"📦 开始打包 AIOS Dashboard {VERSION}...")

# 1. 复制核心文件
print("📄 复制核心文件...")
files_to_copy = [
    ('index.html', 'index.html'),
    ('real_data_server.py', 'server.py'),
]

for src, dst in files_to_copy:
    src_path = DASHBOARD_DIR / src
    dst_path = PACKAGE_DIR / dst
    if src_path.exists():
        shutil.copy2(src_path, dst_path)
        print(f"  ✓ {dst}")

# 2. 创建 README
print("📝 生成 README...")
readme_content = f"""# AIOS Dashboard {VERSION}

## 快速开始

### Windows
```cmd
python server.py
```

### Linux/Mac
```bash
python3 server.py
```

然后打开浏览器访问：http://localhost:8888

## 功能特性

- ✅ 实时监控 AIOS 系统状态
- ✅ Agent 状态管理
- ✅ Evolution Score 趋势
- ✅ 错误统计和慢操作分析
- ✅ 系统资源监控
- ✅ 手动触发进化
- ✅ Agent 启动/停止控制

## 数据来源

Dashboard 会自动读取以下数据：
1. `../agent_system/data/agents/*.json` - Agent 状态
2. `../../events.jsonl` - 事件日志
3. `../learning/metrics_history.jsonl` - 历史指标

如果没有真实数据，会显示演示数据。

## 系统要求

- Python 3.8+
- psutil（可选，用于系统资源监控）

安装依赖：
```bash
pip install psutil
```

## 端口配置

默认端口：8888

修改端口：编辑 `server.py`，修改 `PORT = 8888`

## 技术栈

- 前端：HTML + Tailwind CSS + Chart.js
- 后端：Python http.server
- 数据更新：轮询模式（每 3 秒）

## 版本信息

- 版本：{VERSION}
- 发布日期：{datetime.now().strftime('%Y-%m-%d')}
- 作者：AIOS Team

## 许可证

MIT License
"""

with open(PACKAGE_DIR / 'README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)
print("  ✓ README.md")

# 3. 创建启动脚本
print("🚀 生成启动脚本...")

# Windows 启动脚本
start_bat = """@echo off
chcp 65001 > nul
echo ========================================
echo   AIOS Dashboard v3.4
echo ========================================
echo.
echo 启动中...
python server.py
pause
"""
with open(PACKAGE_DIR / 'start.bat', 'w', encoding='utf-8') as f:
    f.write(start_bat)
print("  ✓ start.bat")

# Linux/Mac 启动脚本
start_sh = """#!/bin/bash
echo "========================================"
echo "  AIOS Dashboard v3.4"
echo "========================================"
echo ""
echo "启动中..."
python3 server.py
"""
with open(PACKAGE_DIR / 'start.sh', 'w', encoding='utf-8') as f:
    f.write(start_sh)
print("  ✓ start.sh")

# 4. 创建 requirements.txt
print("📋 生成 requirements.txt...")
requirements = """# AIOS Dashboard 依赖
psutil>=5.9.0  # 系统资源监控（可选）
"""
with open(PACKAGE_DIR / 'requirements.txt', 'w', encoding='utf-8') as f:
    f.write(requirements)
print("  ✓ requirements.txt")

# 5. 创建 ZIP 包
print("🗜️  压缩打包...")
zip_path = DASHBOARD_DIR / f"{PACKAGE_NAME}.zip"
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in PACKAGE_DIR.rglob('*'):
        if file.is_file():
            arcname = file.relative_to(PACKAGE_DIR.parent)
            zipf.write(file, arcname)
            
print(f"  ✓ {zip_path.name}")

# 6. 统计信息
total_size = sum(f.stat().st_size for f in PACKAGE_DIR.rglob('*') if f.is_file())
zip_size = zip_path.stat().st_size
file_count = len(list(PACKAGE_DIR.rglob('*')))

print("\n" + "="*50)
print(f"✅ 打包完成！")
print("="*50)
print(f"📦 包名：{PACKAGE_NAME}.zip")
print(f"📁 文件数：{file_count}")
print(f"💾 原始大小：{total_size / 1024:.2f} KB")
print(f"🗜️  压缩后：{zip_size / 1024:.2f} KB")
print(f"📍 位置：{zip_path}")
print("="*50)
print("\n使用方法：")
print(f"1. 解压 {PACKAGE_NAME}.zip")
print(f"2. 进入 {PACKAGE_NAME} 目录")
print("3. 运行 start.bat (Windows) 或 start.sh (Linux/Mac)")
print("4. 打开浏览器访问 http://localhost:8888")
