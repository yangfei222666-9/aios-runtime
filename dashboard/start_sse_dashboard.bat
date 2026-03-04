@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 启动 AIOS Dashboard (SSE 实时推送)
echo ========================================
echo.

cd /d "%~dp0"

echo 📡 启动 SSE 服务器...
"C:\Program Files\Python312\python.exe" sse_server.py 8080

pause
