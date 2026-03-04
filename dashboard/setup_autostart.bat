@echo off
chcp 65001 > nul
echo ========================================
echo   设置 AIOS Dashboard 开机自启
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 需要管理员权限！
    echo 请右键点击此脚本，选择"以管理员身份运行"
    pause
    exit /b 1
)

REM 设置路径
set SCRIPT_DIR=%~dp0
set PYTHON_PATH=C:\Program Files\Python312\python.exe
set SERVER_PATH=%SCRIPT_DIR%real_data_server.py
set TASK_NAME=AIOS-Dashboard

echo [1/3] 检查 Python...
if not exist "%PYTHON_PATH%" (
    echo [错误] 找不到 Python: %PYTHON_PATH%
    pause
    exit /b 1
)
echo   ✓ Python 已找到

echo.
echo [2/3] 创建任务计划...
schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHON_PATH%\" -X utf8 \"%SERVER_PATH%\"" /sc onlogon /rl highest /f
if %errorLevel% neq 0 (
    echo [错误] 创建任务失败！
    pause
    exit /b 1
)
echo   ✓ 任务计划已创建

echo.
echo [3/3] 验证任务...
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 任务验证失败！
    pause
    exit /b 1
)
echo   ✓ 任务验证成功

echo.
echo ========================================
echo   ✅ 设置完成！
echo ========================================
echo.
echo Dashboard 将在下次登录时自动启动
echo 访问地址: http://localhost:8888
echo.
echo 管理命令:
echo   - 查看任务: schtasks /query /tn "%TASK_NAME%"
echo   - 删除任务: schtasks /delete /tn "%TASK_NAME%" /f
echo   - 立即运行: schtasks /run /tn "%TASK_NAME%"
echo.
pause
