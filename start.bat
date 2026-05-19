@echo off
title SportEventsWeb – Setup ^& Launch
color 0A
cd /d "%~dp0"

echo.
echo  =====================================================
echo   SportEventsWeb – One-Click Setup ^& Launch
echo  =====================================================
echo.

:: ── Step 1: Check Python ──────────────────────────────────────────────────
echo  [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERROR] Python is not installed or not in PATH.
    echo  Please install Python 3.10+ from https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo         Found: %%v

:: ── Step 2: Create virtual environment ───────────────────────────────────
echo.
echo  [2/5] Setting up virtual environment...
if not exist "backend\venv\Scripts\activate.bat" (
    echo         Creating new virtual environment...
    python -m venv backend\venv
    if errorlevel 1 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo         Virtual environment created.
) else (
    echo         Virtual environment already exists.
)

:: ── Step 3: Activate venv ────────────────────────────────────────────────
call backend\venv\Scripts\activate.bat

:: ── Step 4: Install dependencies ─────────────────────────────────────────
echo.
echo  [3/5] Installing Python dependencies...
echo         (this may take a minute on first run)
echo.
pip install --upgrade pip -q
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo.
    echo  [ERROR] Dependency installation failed. Check your internet connection.
    pause
    exit /b 1
)
echo.
echo         All dependencies installed successfully.

:: ── Step 5: Environment file ──────────────────────────────────────────────
echo.
echo  [4/5] Checking environment configuration...
if not exist "backend\.env" (
    copy backend\.env.example backend\.env >nul
    echo.
    echo  ┌─────────────────────────────────────────────────────────┐
    echo  │  IMPORTANT: First-time setup required!                  │
    echo  │                                                         │
    echo  │  A backend\.env file has been created for you.          │
    echo  │  Please edit it with your settings before continuing:   │
    echo  │                                                         │
    echo  │    DB_PASSWORD    - your MySQL root password            │
    echo  │    SECRET_KEY     - run: python -c "import secrets;     │
    echo  │                     print(secrets.token_hex(32))"       │
    echo  │    SMTP_USER      - your Gmail address                  │
    echo  │    SMTP_PASSWORD  - your Gmail App Password             │
    echo  │                                                         │
    echo  │  See README.md for full setup instructions.             │
    echo  └─────────────────────────────────────────────────────────┘
    echo.
    echo  Press any key after editing backend\.env to continue...
    pause >nul
) else (
    echo         backend\.env found.
)

:: ── Start server ──────────────────────────────────────────────────────────
echo.
echo  [5/5] Starting server...
echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║                                                      ║
echo  ║   SportEventsWeb API is running!                     ║
echo  ║                                                      ║
echo  ║   Backend  :  http://localhost:8000                  ║
echo  ║   API Docs :  http://localhost:8000/docs             ║
echo  ║   Frontend :  open frontend\index.html in browser    ║
echo  ║                                                      ║
echo  ║   Press CTRL+C to stop the server                    ║
echo  ║                                                      ║
echo  ╚══════════════════════════════════════════════════════╝
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
