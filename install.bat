@echo off
chcp 65001 >nul
echo ======================================================================
echo AIOS - AI Operating System
echo One-Click Installer for Windows
echo ======================================================================
echo.

:: Check Python version
echo [1/5] Checking Python version...
"C:\Program Files\Python312\python.exe" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found at C:\Program Files\Python312\python.exe
    echo Please update the path in install.bat or install Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('"C:\Program Files\Python312\python.exe" --version 2^>^&1') do set PYTHON_VERSION=%%i
echo     Found Python %PYTHON_VERSION%

:: Check Python 3.8+
"C:\Program Files\Python312\python.exe" -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.8+ required. Found %PYTHON_VERSION%
    pause
    exit /b 1
)
echo     [OK] Python version compatible

:: Check pip
echo.
echo [2/5] Checking pip...
"C:\Program Files\Python312\python.exe" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found. Please install pip.
    pause
    exit /b 1
)
echo     [OK] pip available

:: Install optional dependencies
echo.
echo [3/5] Installing optional dependencies...
"C:\Program Files\Python312\python.exe" -m pip install aiosqlite --quiet 2>nul
if errorlevel 1 (
    echo     [WARN] aiosqlite not installed (optional, for Storage Manager)
) else (
    echo     [OK] aiosqlite installed
)

:: Verify AIOS files
echo.
echo [4/5] Verifying AIOS files...
if not exist "aios.py" (
    echo [ERROR] aios.py not found. Please run this script from the AIOS directory.
    pause
    exit /b 1
)
echo     [OK] aios.py found

if not exist "core\event_bus.py" (
    echo [ERROR] core\event_bus.py not found. AIOS installation may be incomplete.
    pause
    exit /b 1
)
echo     [OK] Core modules found

if not exist "agent_system\agents.json" (
    echo [WARN] agent_system\agents.json not found. Creating default...
    mkdir agent_system 2>nul
    echo {"agents": [], "metadata": {"last_updated": ""}} > agent_system\agents.json
)
echo     [OK] Agent system ready

:: Run quick test
echo.
echo [5/5] Running quick test...
"C:\Program Files\Python312\python.exe" -X utf8 aios.py version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] AIOS test failed. Please check the installation.
    pause
    exit /b 1
)
echo     [OK] AIOS test passed

:: Done
echo.
echo ======================================================================
echo Installation Complete!
echo ======================================================================
echo.
echo Quick Start:
echo   "C:\Program Files\Python312\python.exe" aios.py demo --scenario 1
echo   "C:\Program Files\Python312\python.exe" aios.py submit --desc "My task" --type code --priority high
echo   "C:\Program Files\Python312\python.exe" aios.py tasks
echo   "C:\Program Files\Python312\python.exe" aios.py heartbeat
echo   "C:\Program Files\Python312\python.exe" aios.py dashboard
echo.
echo Documentation: README.md
echo ======================================================================
echo.
