@echo off
chcp 65001 >nul
echo ========================================
echo AIOS 依赖安装器
echo ========================================
echo.
echo 正在检查 Python...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python！
    echo 请先安装 Python 3.8+
    pause
    exit /b 1
)

echo.
echo 正在安装依赖...
pip install -r requirements.txt

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步: 双击 run.bat 运行演示
echo.
pause
