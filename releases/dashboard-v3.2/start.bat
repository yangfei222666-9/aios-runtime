@echo off
chcp 65001 >nul
echo ========================================
echo   AIOS Dashboard v3.2
echo   实时控制中心
echo ========================================
echo.
echo 正在启动服务器...
echo.

cd /d "%~dp0"
start /B "" "python" server.py

timeout /t 2 >nul

echo ✓ 服务器已启动（后台运行）
echo.
echo 访问地址: http://127.0.0.1:9091
echo.
echo 按任意键打开浏览器...
pause >nul

start http://127.0.0.1:9091
