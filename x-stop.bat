@echo off
echo Stopping Aurora services...

:: Kill processes on Aurora ports (only 5000 and 5002 now)
for %%p in (5000 5002) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p ^| findstr LISTENING') do (
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo Aurora services stopped.
