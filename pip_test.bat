@echo off
cd /d "%~dp0"
pip show uvicorn >nul 2>&1
if errorlevel 1 (echo MISSING) else (echo PRESENT)
echo DONE
