@echo off
cd /d "%~dp0"
start /B pythonw "C:\Program Files\Python312\python.exe" server.py
echo Dashboard 已在后台启动
echo 访问: http://127.0.0.1:9091
timeout /t 3 >nul
