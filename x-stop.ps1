# Aurora Universal Stop Command - PowerShell Wrapper
# This script ensures we're in the correct directory and runs the Python script

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "[AURORA] Stopping from: $ScriptDir" -ForegroundColor Cyan

if (Test-Path "x-stop.py") {
    python x-stop.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] Failed to stop Aurora services" -ForegroundColor Red
        Write-Host "[INFO] Make sure Python is installed and in your PATH" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[ERROR] x-stop.py not found in: $ScriptDir" -ForegroundColor Red
    Write-Host "[INFO] Make sure you're in the Aurora-x project directory" -ForegroundColor Yellow
    exit 1
}
