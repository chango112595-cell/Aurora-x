@echo off
REM Aurora Desktop App Launcher for Windows
cd /d "%~dp0"
python aurora-desktop.py
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start Aurora Desktop App
    echo [INFO] Make sure Python is installed and tkinter is available
    pause
    exit /b 1
)
