# AIOS 跨平台部署指南

本文档介绍如何在不同操作系统上部署 AIOS。

---

## 支持的平台

- ✅ **Windows 10/11** (x64, ARM64)
- ✅ **macOS 11+** (Intel, Apple Silicon)
- ✅ **Linux** (Ubuntu 20.04+, Debian 11+, CentOS 8+, Arch Linux)

---

## 快速安装

### Windows

```powershell
# 下载项目
git clone https://github.com/YOUR_USERNAME/aios.git
cd aios

# 运行安装脚本
.\install_windows.bat
```

### macOS / Linux

```bash
# 下载项目
git clone https://github.com/YOUR_USERNAME/aios.git
cd aios

# 添加执行权限
chmod +x install_unix.sh

# 运行安装脚本
./install_unix.sh
```

---

## 手动安装

### 1. 安装 Python 3.8+

**Windows:**
- 下载：https://www.python.org/downloads/
- 安装时勾选 "Add Python to PATH"

**macOS:**
```bash
# 使用 Homebrew
brew install python@3.12
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install python3 python3-pip
```

### 2. 创建虚拟环境（推荐）

```bash
# 所有平台通用
python3 -m venv venv

# Windows 激活
venv\Scripts\activate.bat

# macOS/Linux 激活
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 升级 pip
python -m pip install --upgrade pip

# 安装 AIOS
pip install -r requirements.txt

# 或从源码安装
pip install -e .
```

### 4. 初始化配置

```bash
# 创建必要的目录
python -c "from platform_adapter import get_adapter; get_adapter().create_directories()"

# 复制配置文件
cp config.yaml.example config.yaml

# 编辑配置
# Windows: notepad config.yaml
# macOS: open -e config.yaml
# Linux: nano config.yaml
```

---

## 平台特定配置

### Windows

**目录结构：**
```
%APPDATA%\aios\          # 配置文件
%LOCALAPPDATA%\aios\     # 数据和缓存
%LOCALAPPDATA%\aios\logs # 日志文件
```

**开机自启动：**
```powershell
# 手动创建启动脚本
$StartupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\aios.bat"
@"
@echo off
cd /d "C:\path\to\aios"
python aios.py start
"@ | Out-File -FilePath $StartupPath -Encoding ASCII
```

**防火墙规则：**
```powershell
# 允许 Dashboard 端口（8888）
New-NetFirewallRule -DisplayName "AIOS Dashboard" -Direction Inbound -LocalPort 8888 -Protocol TCP -Action Allow
```

### macOS

**目录结构：**
```
~/Library/Application Support/aios/      # 配置和数据
~/Library/Caches/aios/                   # 缓存
~/Library/Logs/aios/                     # 日志
```

**开机自启动（LaunchAgent）：**
```bash
# 创建 plist 文件
cat > ~/Library/LaunchAgents/com.aios.agent.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aios.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/aios/aios.py</string>
        <string>start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# 加载服务
launchctl load ~/Library/LaunchAgents/com.aios.agent.plist

# 启动服务
launchctl start com.aios.agent
```

**权限设置：**
```bash
# 允许终端访问（首次运行时会提示）
# 系统偏好设置 > 安全性与隐私 > 隐私 > 完全磁盘访问权限
```

### Linux

**目录结构：**
```
~/.config/aios/          # 配置文件
~/.local/share/aios/     # 数据文件
~/.cache/aios/           # 缓存文件
~/.local/share/aios/logs # 日志文件
```

**开机自启动（systemd）：**
```bash
# 创建 systemd 服务
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/aios.service << 'EOF'
[Unit]
Description=AIOS Agent System
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/aios/aios.py start
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

# 重载配置
systemctl --user daemon-reload

# 启用服务
systemctl --user enable aios.service

# 启动服务
systemctl --user start aios.service

# 查看状态
systemctl --user status aios.service
```

**开机自启动（cron）：**
```bash
# 编辑 crontab
crontab -e

# 添加以下行
@reboot cd /path/to/aios && /usr/bin/python3 aios.py start
```

---

## 验证安装

### 🔑 最小验证清单（安装后 3 条命令）

安装完成后，依次运行以下 3 条命令确认一切正常：

```bash
# ① 确认服务可用（输出平台信息即成功）
python platform_adapter.py

# ② 确认日志路径存在（输出绝对路径 + 目录已创建）
python -c "from platform_adapter import get_adapter; a=get_adapter(); a.create_directories(); print('Log dir:', a.get_log_dir())"

# ③ 确认测试全绿（19 passed, 2 skipped, 0 warnings）
python -m pytest tests/test_platform_adapter.py -v
```

**预期结果：**

| 命令 | 成功标志 |
|------|----------|
| ① `platform_adapter.py` | 输出 `[Platform Info]` + `[Directories]` + `[Shell]` |
| ② 日志路径 | 输出 `Log dir: <绝对路径>`，路径目录已存在 |
| ③ 测试套件 | `19 passed, 2 skipped` 且 0 warnings |

如果三条命令全部通过，安装验证完成。

---

### 1. 检查平台信息

```bash
python platform_adapter.py
```

**预期输出：**
```
==============================================================
AIOS Platform Adapter
==============================================================

[Platform Info]
  system: Windows / Darwin / Linux
  machine: x86_64 / arm64
  python_version: 3.12.0
  platform: Windows-10-... / macOS-14.0-... / Linux-6.5.0-...

[System Info]
  cpu: Intel Core i7 / Apple M2 / AMD Ryzen 7
  memory: 32.0 GB

[Directories]
  Config: /path/to/config
  Data: /path/to/data
  Cache: /path/to/cache
  Log: /path/to/logs

[Startup Script]
  Path: /path/to/startup/script

[Shell]
  Command: powershell / bash
  Python: /path/to/python

==============================================================
```

### 2. 运行测试

```bash
# 运行单元测试
python -m pytest tests/

# 运行 Demo
python aios.py demo
```

### 3. 启动 Dashboard

```bash
# 启动 AIOS
python aios.py start

# 访问 Dashboard
# http://127.0.0.1:8888
```

---

## 常见问题

### Windows

**Q: PowerShell 执行策略错误**
```powershell
# 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 永久允许（需要管理员权限）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Q: 中文乱码**
```powershell
# 设置 UTF-8 编码
$env:PYTHONUTF8=1
$env:PYTHONIOENCODING='utf-8'
```

**Q: 端口被占用**
```powershell
# 查找占用端口的进程
netstat -ano | findstr :8888

# 杀死进程
taskkill /F /PID <PID>
```

### macOS

**Q: 权限被拒绝**
```bash
# 添加执行权限
chmod +x install_unix.sh
chmod +x aios.py
```

**Q: Python 版本冲突**
```bash
# 使用 pyenv 管理多个 Python 版本
brew install pyenv
pyenv install 3.12.0
pyenv local 3.12.0
```

**Q: LaunchAgent 不工作**
```bash
# 检查日志
tail -f ~/Library/Logs/aios/stderr.log

# 重新加载
launchctl unload ~/Library/LaunchAgents/com.aios.agent.plist
launchctl load ~/Library/LaunchAgents/com.aios.agent.plist
```

### Linux

**Q: Python 版本过低**
```bash
# Ubuntu 20.04 安装 Python 3.12
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
```

**Q: systemd 服务失败**
```bash
# 查看日志
journalctl --user -u aios.service -f

# 检查服务状态
systemctl --user status aios.service

# 重启服务
systemctl --user restart aios.service
```

**Q: 端口被占用**
```bash
# 查找占用端口的进程
sudo lsof -i :8888

# 杀死进程
kill -9 <PID>
```

---

## 卸载

### Windows

```powershell
# 停止服务
python aios.py stop

# 删除启动脚本
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\aios.bat"

# 删除数据（可选）
rmdir /s /q "%APPDATA%\aios"
rmdir /s /q "%LOCALAPPDATA%\aios"

# 卸载 Python 包
pip uninstall aios-framework
```

### macOS

```bash
# 停止服务
launchctl stop com.aios.agent
launchctl unload ~/Library/LaunchAgents/com.aios.agent.plist

# 删除服务文件
rm ~/Library/LaunchAgents/com.aios.agent.plist

# 删除数据（可选）
rm -rf ~/Library/Application\ Support/aios
rm -rf ~/Library/Caches/aios
rm -rf ~/Library/Logs/aios

# 卸载 Python 包
pip uninstall aios-framework
```

### Linux

```bash
# 停止服务
systemctl --user stop aios.service
systemctl --user disable aios.service

# 删除服务文件
rm ~/.config/systemd/user/aios.service
systemctl --user daemon-reload

# 删除数据（可选）
rm -rf ~/.config/aios
rm -rf ~/.local/share/aios
rm -rf ~/.cache/aios

# 卸载 Python 包
pip uninstall aios-framework
```

---

## 技术支持

- **文档：** https://github.com/YOUR_USERNAME/aios#readme
- **问题反馈：** https://github.com/YOUR_USERNAME/aios/issues
- **讨论区：** https://github.com/YOUR_USERNAME/aios/discussions

---

**最后更新：** 2026-03-06  
**版本：** v1.0
