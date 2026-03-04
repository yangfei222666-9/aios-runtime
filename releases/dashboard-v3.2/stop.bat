@echo off
chcp 65001 >nul
echo 正在停止 Dashboard 服务器...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9091 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
    echo ✓ 服务器已停止 (PID: %%a)
)

timeout /t 2 >nul
