@echo off
echo 安装网页图片采集器所需依赖...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 检测到Python，开始安装依赖包...
echo.

REM 升级pip
python -m pip install --upgrade pip

REM 安装依赖
python -m pip install -r requirements.txt

echo.
echo 依赖安装完成！
echo.
echo 运行程序请双击 run.bat 或在命令行中输入: python image_scraper.py
echo.
pause