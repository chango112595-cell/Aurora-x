@echo off
cd /d C:\Users\negry\Aurora-x

:: Activate venv FIRST
call importcheck.venv\Scripts\activate.bat

:: Now run Aurora with the activated venv
python x-start.py %*

echo.
echo To stop all services, run: x-stop
pause
