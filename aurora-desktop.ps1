# Aurora Desktop App Launcher for PowerShell
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "[AURORA] Starting Desktop App..." -ForegroundColor Cyan

if (Test-Path "aurora-desktop.py") {
    python aurora-desktop.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] Failed to start Aurora Desktop App" -ForegroundColor Red
        Write-Host "[INFO] Make sure Python is installed and tkinter is available" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "[ERROR] aurora-desktop.py not found" -ForegroundColor Red
    exit 1
}
