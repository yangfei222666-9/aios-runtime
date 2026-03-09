@echo off
REM AIOS 安装脚本 - Windows 版本

echo ==================================
echo AIOS Installation - Windows
echo ==================================

REM 检查 Python 版本
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.8+ is required but not found
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM 检查 Python 版本是否 >= 3.8
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.8+ is required (found %PYTHON_VERSION%)
    pause
    exit /b 1
)

REM 询问是否创建虚拟环境
set /p CREATE_VENV="Create virtual environment? (y/n): "
if /i "%CREATE_VENV%"=="y" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Virtual environment created and activated
) else (
    echo [1/5] Skipping virtual environment
)

REM 升级 pip
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip

REM 安装依赖
echo [3/5] Installing dependencies...
if exist requirements.txt (
    python -m pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt not found, installing from setup.py
    python -m pip install -e .
)

REM 创建必要的目录
echo [4/5] Creating directories...
python -c "from platform_adapter import get_adapter; get_adapter().create_directories()"
echo Directories created

REM 初始化配置
echo [5/5] Initializing configuration...
if not exist config.yaml (
    (
        echo # AIOS Configuration
        echo.
        echo # Agent System
        echo agents:
        echo   enabled: true
        echo   max_workers: 5
        echo   timeout: 120
        echo.
        echo # Event Bus
        echo event_bus:
        echo   enabled: true
        echo   max_queue_size: 1000
        echo.
        echo # Logging
        echo logging:
        echo   level: INFO
        echo   file: logs/aios.log
        echo.
        echo # Dashboard
        echo dashboard:
        echo   enabled: true
        echo   host: 127.0.0.1
        echo   port: 8888
        echo.
        echo # Telegram ^(optional^)
        echo telegram:
        echo   enabled: false
        echo   bot_token: ""
        echo   chat_id: ""
    ) > config.yaml
    echo Default config.yaml created
) else (
    echo config.yaml already exists
)

echo.
echo ==================================
echo Installation completed!
echo ==================================
echo.
echo Next steps:
echo   1. Edit config.yaml to configure AIOS
echo   2. Run: python aios.py --help
echo   3. Start AIOS: python aios.py start
echo.

REM 询问是否设置开机自启动
set /p SETUP_AUTOSTART="Setup auto-start on boot? (y/n): "
if /i "%SETUP_AUTOSTART%"=="y" (
    echo Setting up auto-start...
    
    REM 获取当前目录
    set AIOS_DIR=%CD%
    
    REM 创建启动脚本
    set STARTUP_SCRIPT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\aios.bat
    
    (
        echo @echo off
        echo cd /d "%AIOS_DIR%"
        echo python aios.py start
    ) > "%STARTUP_SCRIPT%"
    
    echo Auto-start script created: %STARTUP_SCRIPT%
    echo AIOS will start automatically on next boot
)

echo.
echo Installation complete! 🎉
pause
