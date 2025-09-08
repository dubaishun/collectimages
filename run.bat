@echo off
echo 启动网页图片采集器...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先运行 install.bat 安装依赖
    pause
    exit /b 1
)

REM 运行程序
python image_scraper.py

pause