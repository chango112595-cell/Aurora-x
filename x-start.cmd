@echo off
REM Universal Aurora Start Command - Works on Windows
REM This file allows you to type "x-start" without extension

cd /d "%~dp0"
python x-start.py %*
