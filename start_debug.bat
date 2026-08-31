@echo on
title Flare Project Launcher
cd /d "%~dp0"

echo ==========================================
echo        Starting Flare Project
echo ==========================================
echo.

echo Checking prerequisites...

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download from https://www.python.org/downloads/
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
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

echo Checking backend dependencies...
pip show uvicorn >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing backend dependencies (first run may take a few minutes)...
    python -m pip install -r "%~dp0backend\requirements.txt"
    if errorlevel 1 (
        echo [ERROR] Failed to install backend dependencies.
        pause
        exit /b 1
    )
) else (
    echo Backend dependencies already installed.
)
echo.

echo Freeing ports 8000 and 5174 if occupied...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5174" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo.

echo [1/2] Starting backend server (port 8000)...
start "Flare Backend" cmd /k "cd /d "%~dp0backend" && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting frontend server (port 5174)...
start "Flare Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Waiting 8 seconds for servers to start...
timeout /t 8 /nobreak >nul

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
