@echo off
REM Aurora Universal Start Command - Windows Batch Wrapper
REM This script ensures we're in the correct directory and runs the Python script

cd /d "%~dp0"
echo [AURORA] Starting from: %CD%

if not exist "x-start.py" (
    echo [ERROR] x-start.py not found in: %CD%
    echo [INFO] Make sure you're in the Aurora-x project directory
    pause
    exit /b 1
)

python x-start.py
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start Aurora services
    echo [INFO] Make sure Python is installed and in your PATH
    echo [INFO] Try: python --version
    pause
    exit /b 1
)
