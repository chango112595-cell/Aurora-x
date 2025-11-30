<#
installers/install-windows.ps1
Run as Administrator for service install actions.
#>
param(
  [string]$Root = (Split-Path -Parent $MyInvocation.MyCommand.Definition),
  [string]$Token = "aurora-dev-token",
  [switch]$InstallService
)

Write-Host "Aurora Windows installer - root: $Root"

# ensure python present
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Host "Install Python 3 and add to PATH" -ForegroundColor Yellow
  exit 1
}

python -m pip install --upgrade pip
python -m pip install fastapi uvicorn[standard] psutil watchdog websockets

if (Get-Command npm -ErrorAction SilentlyContinue) {
  Push-Location $Root
  npm ci
  npm i -g tsx
  Pop-Location
}

New-Item -ItemType Directory -Path "$Root\aurora_logs" -Force | Out-Null
New-Item -ItemType Directory -Path "$Root\.aurora\pids" -Force | Out-Null
Set-Content -Path "$Root\.aurora\api.token" -Value $Token -Force

if ($InstallService) {
  Write-Host "Installing Windows service via NSSM (please have nssm in PATH)"
  $nssm = "nssm"
  if (-not (Get-Command $nssm -ErrorAction SilentlyContinue)) {
    Write-Host "NSSM not found. Download from https://nssm.cc/ and put nssm.exe in PATH" -ForegroundColor Yellow
    exit 1
  }
  $svcname = "AuroraOS"
  & $nssm install $svcname (Get-Command python).Source "$Root\aurora_os.py start"
  & $nssm set $svcname AppDirectory $Root
  & $nssm start $svcname
  Write-Host "Service installed and started"
}
Write-Host "Install complete. Start with .\\aurora.ps1 start"
