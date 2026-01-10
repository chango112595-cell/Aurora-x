@echo off
REM Aurora Universal Stop Command - Windows Batch Wrapper
REM This script ensures we're in the correct directory and runs the Python script

cd /d "%~dp0"
echo [AURORA] Stopping from: %CD%

if not exist "x-stop.py" (
    echo [ERROR] x-stop.py not found in: %CD%
    echo [INFO] Make sure you're in the Aurora-x project directory
    pause
    exit /b 1
)

python x-stop.py
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to stop Aurora services
    echo [INFO] Make sure Python is installed and in your PATH
    pause
    exit /b 1
)
