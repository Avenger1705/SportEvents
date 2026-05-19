@echo off
title Sport Events – Backend Server
cd /d "%~dp0"

:: Create virtual environment if missing
if not exist "backend\venv\Scripts\activate.bat" (
    echo [*] Creating virtual environment...
    python -m venv backend\venv
)

:: Activate
call backend\venv\Scripts\activate.bat

:: Install / upgrade dependencies
echo [*] Installing dependencies...
pip install -q -r backend\requirements.txt

:: Copy .env if not present
if not exist "backend\.env" (
    copy backend\.env.example backend\.env
    echo [!] backend\.env created from backend\.env.example – please edit it before using the app.
    pause
)

:: Start server
echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   Sport Events API  –  http://localhost:8000  ║
echo  ╚══════════════════════════════════════════╝
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
