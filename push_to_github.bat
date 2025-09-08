@echo off
echo ===============================================
echo 网页图片采集器 - GitHub推送脚本
echo ===============================================
echo.

REM 检查Git是否安装
git --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Git，请先安装Git
    echo 下载地址: https://git-scm.com/
    pause
    exit /b 1
)

echo 检测到Git，开始推送流程...
echo.

REM 进入项目目录
cd /d "%~dp0"

echo 1. 初始化Git仓库...
git init

echo.
echo 2. 添加所有文件...
git add .

echo.
echo 3. 创建初始提交...
git commit -m "🎉 Initial release: Web Image Scraper v1.0

✨ Features:
- Smart image detection and filtering
- GUI interface with tkinter
- Sequential image downloading  
- Image preview functionality
- Progress monitoring and logging
- Multi-format support
- Responsive and centered window display

🛠️ Technical Stack:
- Python 3.7+, tkinter, requests, BeautifulSoup4, Pillow

📄 License: MIT
👨‍💻 Author: 速光网络软件开发 (suguang.cc)"

echo.
echo 4. 添加远程仓库...
git remote add origin https://github.com/dubaishun/collectimages.git

echo.
echo 5. 设置主分支...
git branch -M main

echo.
echo 6. 准备推送到GitHub...
echo ===============================================
echo 重要提示:
echo 1. 接下来会提示输入GitHub用户名和密码
echo 2. 用户名: 输入您的GitHub用户名 (dubaishun)
echo 3. 密码: 输入您的Personal Access Token (不是GitHub密码!)
echo.
echo 如果您还没有Personal Access Token:
echo 1. 访问 https://github.com/settings/tokens
echo 2. 点击 "Generate new token (classic)"
echo 3. 选择 "repo" 权限
echo 4. 复制生成的token
echo ===============================================
echo.
pause

echo 开始推送...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ❌ 推送失败！可能的原因：
    echo 1. 身份验证失败 - 请确认使用Personal Access Token
    echo 2. 网络连接问题
    echo 3. 仓库权限问题
    echo.
    echo 请查看错误信息并参考 GIT_PUSH_GUIDE.md 文档
) else (
    echo.
    echo ✅ 推送成功！
    echo 您的代码已上传到: https://github.com/dubaishun/collectimages
    echo.
    echo 建议接下来的操作：
    echo 1. 访问仓库页面检查文件是否正确
    echo 2. 添加仓库描述和标签
    echo 3. 创建Release版本
)

echo.
pause