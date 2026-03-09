#!/bin/bash
# AIOS 安装脚本 - macOS/Linux 版本

set -e

echo "=================================="
echo "AIOS Installation - macOS/Linux"
echo "=================================="

# 检测操作系统
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=macOS;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "Detected platform: ${PLATFORM}"

# 检查 Python 版本
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3.8+ is required but not found"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Python version: ${PYTHON_VERSION}"

# 检查 Python 版本是否 >= 3.8
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "[ERROR] Python 3.8+ is required (found ${PYTHON_VERSION})"
    exit 1
fi

# 创建虚拟环境（可选）
read -p "Create virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "[1/5] Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
else
    echo "[1/5] Skipping virtual environment"
fi

# 升级 pip
echo "[2/5] Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip

# 安装依赖
echo "[3/5] Installing dependencies..."
if [ -f "requirements.txt" ]; then
    $PYTHON_CMD -m pip install -r requirements.txt
else
    echo "[WARNING] requirements.txt not found, installing from setup.py"
    $PYTHON_CMD -m pip install -e .
fi

# 创建必要的目录
echo "[4/5] Creating directories..."
$PYTHON_CMD -c "from platform_adapter import get_adapter; get_adapter().create_directories()"
echo "✓ Directories created"

# 初始化配置
echo "[5/5] Initializing configuration..."
if [ ! -f "config.yaml" ]; then
    cat > config.yaml << 'EOF'
# AIOS Configuration

# Agent System
agents:
  enabled: true
  max_workers: 5
  timeout: 120

# Event Bus
event_bus:
  enabled: true
  max_queue_size: 1000

# Logging
logging:
  level: INFO
  file: logs/aios.log

# Dashboard
dashboard:
  enabled: true
  host: 127.0.0.1
  port: 8888

# Telegram (optional)
telegram:
  enabled: false
  bot_token: ""
  chat_id: ""
EOF
    echo "✓ Default config.yaml created"
else
    echo "✓ config.yaml already exists"
fi

echo ""
echo "=================================="
echo "Installation completed!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Edit config.yaml to configure AIOS"
echo "  2. Run: $PYTHON_CMD aios.py --help"
echo "  3. Start AIOS: $PYTHON_CMD aios.py start"
echo ""

# 询问是否设置开机自启动
read -p "Setup auto-start on boot? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ "$PLATFORM" = "macOS" ]; then
        # macOS LaunchAgent
        PLIST_PATH="$HOME/Library/LaunchAgents/com.aios.agent.plist"
        AIOS_PATH="$(pwd)/aios.py"
        
        cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aios.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_CMD</string>
        <string>$AIOS_PATH</string>
        <string>start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/aios/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/aios/stderr.log</string>
</dict>
</plist>
EOF
        
        launchctl load "$PLIST_PATH"
        echo "✓ LaunchAgent installed: $PLIST_PATH"
        
    elif [ "$PLATFORM" = "Linux" ]; then
        # Linux systemd service
        SERVICE_PATH="$HOME/.config/systemd/user/aios.service"
        AIOS_PATH="$(pwd)/aios.py"
        
        mkdir -p "$HOME/.config/systemd/user"
        
        cat > "$SERVICE_PATH" << EOF
[Unit]
Description=AIOS Agent System
After=network.target

[Service]
Type=simple
ExecStart=$PYTHON_CMD $AIOS_PATH start
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF
        
        systemctl --user daemon-reload
        systemctl --user enable aios.service
        echo "✓ Systemd service installed: $SERVICE_PATH"
        echo "  Start: systemctl --user start aios"
        echo "  Stop: systemctl --user stop aios"
        echo "  Status: systemctl --user status aios"
    fi
fi

echo ""
echo "Installation complete! 🎉"
