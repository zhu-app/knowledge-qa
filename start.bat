@echo off
cd /d "%~dp0"
echo ================================
echo   Knowledge QA System - Starting
echo ================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

if not exist ".env" (
    echo [INFO] Creating .env from .env.example...
    copy .env.example .env >nul
    echo [INFO] Please edit .env and add your API Key, then run start.bat again.
    pause
    exit /b 1
)

echo Starting service...
echo Browser will open: http://localhost:8501
echo Press Ctrl+C to stop.
echo.

venv\Scripts\python.exe -m streamlit run app.py --server.port 8501 --server.headless false