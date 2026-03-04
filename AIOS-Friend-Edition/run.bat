@echo off
chcp 65001 >nul
echo ========================================
echo AIOS 演示启动器
echo ========================================
echo.
echo 选择演示场景:
echo   1. 文件监控 + 自动分类
echo   2. API 健康检查 + 自动恢复
echo   3. 日志分析 + 自动生成 Playbook
echo.
set /p choice="请输入场景编号 (1-3): "

if "%choice%"=="1" (
    python aios.py demo --scenario 1
) else if "%choice%"=="2" (
    python aios.py demo --scenario 2
) else if "%choice%"=="3" (
    python aios.py demo --scenario 3
) else (
    echo 无效的选择！
)

echo.
pause
