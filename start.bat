@echo off
title Flare Project Launcher

echo ==========================================
echo        Starting Flare Project
echo ==========================================
echo.

:: ── Check prerequisites ──

echo [0/3] Checking prerequisites...

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo        Python  [OK]

:: Check Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo         Download from https://nodejs.org/
    pause
    exit /b 1
)
echo        Node    [OK]

:: Check npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not available.
    echo         Reinstall Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo        npm     [OK]

:: Check .env exists
if not exist "%~dp0backend\.env" (
    echo [WARNING] backend\.env not found.
    if exist "%~dp0backend\.env.example" (
        echo          Copying .env.example to .env ...
        copy "%~dp0backend\.env.example" "%~dp0backend\.env" >nul 2>&1
        echo          Created .env from template. Fill in your API keys before running.
        pause
        exit /b 1
    ) else (
        echo          No .env or .env.example found. Create backend\.env with your API keys.
        pause
        exit /b 1
    )
)
echo        .env    [OK]

echo.

:: ── Start backend ──

echo [1/3] Starting backend server (port 8000)...
start "Flare Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: Wait for backend to become reachable
echo        Waiting for backend...
set /a _retries=0
:_wait_backend
timeout /t 1 /nobreak >nul
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    set /a _retries+=1
    if %_retries% geq 15 (
        echo [ERROR] Backend did not start within 15 seconds.
        echo         Check the "Flare Backend" window for errors.
        pause
        exit /b 1
    )
    goto _wait_backend
)
echo        Backend [OK] - http://localhost:8000

:: ── Start frontend ──

echo [2/3] Starting frontend server (port 5174)...
start "Flare Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

:: Wait for frontend to become reachable
echo        Waiting for frontend...
set /a _retries=0
:_wait_frontend
timeout /t 1 /nobreak >nul
curl -s http://localhost:5174 >nul 2>&1
if %errorlevel% neq 0 (
    set /a _retries+=1
    if %_retries% geq 15 (
        echo [ERROR] Frontend did not start within 15 seconds.
        echo         Check the "Flare Frontend" window for errors.
        pause
        exit /b 1
    )
    goto _wait_frontend
)
echo        Frontend[OK] - http://localhost:5174

:: ── Open browser ──

echo [3/3] Opening browser...
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
