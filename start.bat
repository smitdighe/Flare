@echo off
title Flare Project Launcher
cd /d "%~dp0"

echo ==========================================
echo        Starting Flare Project
echo ==========================================
echo.

:: ── Check prerequisites ──

echo Checking prerequisites...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download from https://www.python.org/downloads/
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo         Download from https://nodejs.org/
    pause
    exit /b 1
)

if not exist "backend\.env" (
    echo.
    echo [WARNING] backend\.env not found.
    if exist "backend\.env.example" (
        copy "backend\.env.example" "backend\.env" >nul 2>&1
        echo          Created .env from template.
    )
    echo          Fill in your API keys in backend\.env then run this again.
    pause
    exit /b 1
)

echo Prerequisites OK.
echo.

:: ── Start backend ──

echo [1/2] Starting backend server (port 8000)...
start "Flare Backend" cmd /k "cd /d "%cd%\backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting frontend server (port 5174)...
start "Flare Frontend" cmd /k "cd /d "%cd%\frontend" && npm run dev"

:: Wait for servers to start
echo.
echo Waiting 5 seconds for servers to start...
timeout /t 5 /nobreak >nul

:: Open browser
echo Opening browser...
start http://localhost:5174

echo.
echo ==========================================
echo   Flare is running!
echo ==========================================
echo   Backend:   http://localhost:8000
echo   Frontend:  http://localhost:5174
echo ==========================================
echo   Close this window anytime. Server windows stay open.
echo.
pause
