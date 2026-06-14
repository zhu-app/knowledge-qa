@echo off
cd /d "%~dp0"
echo ================================
echo   个人知识库问答系统 - 安装脚本
echo ================================
echo(

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo   下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 创建虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo [1/2] 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
) else (
    echo [1/2] 虚拟环境已存在，跳过
)

call venv\Scripts\activate.bat

:: 安装依赖
echo [2/2] 安装依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)

echo(
echo ================================
echo   安装完成！
echo ================================
echo(
echo 1. 拷贝 .env.example 为 .env 并填入 API Key
echo 2. 运行 start.bat 启动系统
echo(
pause
