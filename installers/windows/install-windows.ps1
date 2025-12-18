<#
installers/windows/install-windows.ps1
Run as Administrator (recommended). Bootstraps Aurora on Windows.
Requires: Chocolatey (optional) or manual Python/Node installation.
#>

param(
  [string]$InstallDir = "C:\Aurora-x",
  [switch]$InstallService,
  [string]$ServiceName = "AuroraOS",
  [string]$Token = "aurora-dev-token"
)

Set-StrictMode -Version Latest

if (-not (Test-Path $InstallDir)) {
  New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

Write-Host "Copying repo to $InstallDir (assumes you run installer from repo root)"
# copy current directory to target (be careful)
$src = (Get-Location).Path
robocopy $src $InstallDir /MIR | Out-Null

# Ensure Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host "Python not found. Installing via Chocolatey (if available)..." -ForegroundColor Yellow
  if (Get-Command choco -ErrorAction SilentlyContinue) {
    choco install -y python
  } else {
    Write-Host "Please install Python 3 manually and ensure 'python' in PATH" -ForegroundColor Red
    exit 1
  }
}

# Create a venv
Push-Location $InstallDir
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn[standard] psutil watchdog requests
# optional: install pm2 equivalent not needed

# Node (optional)
if (Get-Command npm -ErrorAction SilentlyContinue) {
  npm install
  npm i -g tsx
}

# create logs dir
New-Item -ItemType Directory -Path "$InstallDir\aurora_logs" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallDir\.aurora\pids" -Force | Out-Null

# save token
Set-Content -Path "$InstallDir\.aurora\api.token" -Value $Token -Force

# Optional: register service using NSSM
if ($InstallService) {
  if (-not (Get-Command nssm -ErrorAction SilentlyContinue)) {
    Write-Host "NSSM (Non-Sucking Service Manager) not found. Download from https://nssm.cc/ and put it in PATH." -ForegroundColor Yellow
  } else {
    $pythonExe = (Get-Command python).Source
    $exeArgs = "$InstallDir\aurora_os.py start"
    nssm install $ServiceName $pythonExe $exeArgs
    nssm set $ServiceName AppDirectory $InstallDir
    nssm set $ServiceName Start SERVICE_AUTO_START
    nssm start $ServiceName
    Write-Host "Service $ServiceName installed and started via NSSM."
  }
}

Write-Host "Windows install complete. To start manually:"
Write-Host "  PowerShell: cd $InstallDir; .\.venv\Scripts\Activate.ps1; python aurora_os.py start"
Pop-Location
