@echo off
title Flare Project Launcher

echo ==========================================
echo        Starting Flare Project
echo ==========================================
echo.

:: ── Check prerequisites ──

echo [0/3] Checking prerequisites...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo        Python  [OK]

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo         Download from https://nodejs.org/
    pause
    exit /b 1
)
echo        Node    [OK]

npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not available.
    echo         Reinstall Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo        npm     [OK]

if not exist "%~dp0backend\.env" (
    echo.
    echo [WARNING] backend\.env not found.
    if exist "%~dp0backend\.env.example" (
        copy "%~dp0backend\.env.example" "%~dp0backend\.env" >nul 2>&1
        echo          Created .env from template.
    )
    echo          Fill in your API keys in backend\.env then run this again.
    pause
    exit /b 1
)
echo        .env    [OK]

echo.

:: ── Start backend ──

echo [1/3] Starting backend server (port 8000)...
start "Flare Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo        Waiting for backend to start...
set /a _count=0
:_wait_backend
timeout /t 2 /nobreak >nul
powershell -Command "try { $r = Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing -TimeoutSec 3; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo        Backend [OK] - http://localhost:8000
    goto :backend_ready
)
set /a _count+=1
if %_count% geq 10 (
    echo [ERROR] Backend did not start within 20 seconds.
    echo         Check the "Flare Backend" window for errors.
    pause
    exit /b 1
)
goto :_wait_backend
:backend_ready

:: ── Start frontend ──

echo [2/3] Starting frontend server (port 5174)...
start "Flare Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo        Waiting for frontend to start...
set /a _count=0
:_wait_frontend
timeout /t 2 /nobreak >nul
powershell -Command "try { $r = Invoke-WebRequest -Uri http://localhost:5174 -UseBasicParsing -TimeoutSec 3; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo        Frontend[OK] - http://localhost:5174
    goto :frontend_ready
)
set /a _count+=1
if %_count% geq 10 (
    echo [ERROR] Frontend did not start within 20 seconds.
    echo         Check the "Flare Frontend" window for errors.
    pause
    exit /b 1
)
goto :_wait_frontend
:frontend_ready

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
