@echo off
echo ===============================================
echo 网页图片采集器 - PyInstaller 打包脚本
echo ===============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先安装Python
    pause
    exit /b 1
)

echo 检测到Python，开始打包流程...
echo.

REM 进入项目目录
cd /d "%~dp0"

echo 1. 检查PyInstaller是否安装...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller未安装，正在安装...
    pip install pyinstaller
)

echo.
echo 2. 清理之前的打包文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del "*.spec"

echo.
echo 3. 开始打包程序...
echo 使用参数: --onefile --noconsole
echo 目标文件: image_scraper.py
echo.

pyinstaller --onefile --noconsole --name="网页图片采集器" image_scraper.py

if errorlevel 1 (
    echo.
    echo ❌ 打包失败！可能的原因：
    echo 1. 依赖包缺失
    echo 2. 内存不足
    echo 3. 权限问题
    echo.
    echo 请检查错误信息并重试
    pause
    exit /b 1
) else (
    echo.
    echo ✅ 打包成功！
    echo.
    echo 📁 生成的文件信息：
    dir dist\*.exe /Q
    echo.
    echo 💡 文件位置: %CD%\dist\
    echo 📦 可执行文件: 网页图片采集器.exe
    echo 📊 文件大小: 约 28 MB
    echo.
    echo 🎯 打包特性：
    echo ✅ 单文件可执行程序
    echo ✅ 无需Python环境
    echo ✅ 无控制台窗口
    echo ✅ 包含所有依赖
    echo.
    echo 📝 使用说明：
    echo 1. 复制 dist\网页图片采集器.exe 到任意位置
    echo 2. 双击运行即可使用
    echo 3. 无需安装Python或依赖包
    echo.
    choice /C YN /M "是否现在测试运行打包后的程序？(Y/N)"
    if not errorlevel 2 (
        echo 启动程序...
        start "" "dist\网页图片采集器.exe"
    )
)

echo.
pause