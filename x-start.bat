@echo off
REM Aurora Universal Start Command - Windows Batch Wrapper
REM This script ensures we're in the correct directory and runs the Python script

cd /d "%~dp0"
python x-start.py
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start Aurora services
    echo [INFO] Make sure Python is installed and in your PATH
    echo [INFO] Try: python --version
    pause
    exit /b 1
)
