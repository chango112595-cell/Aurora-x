@echo off
REM Kill all Aurora Node processes
REM Usage: scripts\kill-aurora.bat

echo 🔍 Finding Aurora Node processes...

tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I /N "node.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Found Node processes, stopping them...
    taskkill /F /IM node.exe >NUL 2>&1
    timeout /t 2 /nobreak >NUL
    echo ✅ All Node processes stopped
) else (
    echo ✅ No Node processes found
)

echo.
echo Checking port 5000...
netstat -ano | findstr :5000 | findstr LISTENING >NUL
if "%ERRORLEVEL%"=="0" (
    echo ⚠️  Port 5000 is still in use!
    netstat -ano | findstr :5000 | findstr LISTENING
) else (
    echo ✅ Port 5000 is free
)
