# Aurora Nexus Complete Startup Script
# Starts all Nexus systems properly

Write-Host "=" -NoNewline -ForegroundColor Cyan; Write-Host "=".PadRight(68, "=") -ForegroundColor Cyan
Write-Host " AURORA NEXUS STARTUP" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan; Write-Host "=".PadRight(68, "=") -ForegroundColor Cyan
Write-Host ""

$auroraHost = if ($env:AURORA_HOST) { $env:AURORA_HOST } else { "127.0.0.1" }
$baseUrl = if ($env:AURORA_BASE_URL) { $env:AURORA_BASE_URL } else { "http://$auroraHost:5000" }
$luminarUrl = if ($env:AURORA_LUMINAR_URL) { $env:AURORA_LUMINAR_URL } else { "http://$auroraHost:8000" }

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
try {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js detected: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found! Please install Node.js" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[STEP 1] Starting Luminar Nexus V2 (Port $LuminarPort)..." -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------------" -ForegroundColor DarkGray

# Start Luminar Nexus V2 in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..'; python tools\luminar_nexus_v2.py" -WindowStyle Minimized

Write-Host "[OK] Luminar Nexus V2 starting..." -ForegroundColor Green
Start-Sleep -Seconds 3

# Check if Luminar is responding
try {
    $response = Invoke-WebRequest -Uri "$luminarUrl/api/nexus/status" -TimeoutSec 5 -UseBasicParsing
    Write-Host "[OK] Luminar Nexus V2 is responding!" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Luminar Nexus V2 may still be starting..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[STEP 2] Starting Express Backend (Port $AuroraPort)..." -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------------" -ForegroundColor DarkGray

# Check if backend is already running
try {
    $backendCheck = Invoke-WebRequest -Uri "$baseUrl/api/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    Write-Host "[OK] Backend already running on port 5000" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Starting backend server..." -ForegroundColor Cyan
    # Backend should auto-start, but verify
}

Write-Host ""
Write-Host "[STEP 3] Verifying Nexus Integration..." -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------------" -ForegroundColor DarkGray

Start-Sleep -Seconds 2

# Test Luminar routes
Write-Host "[TEST] GET /api/luminar-nexus/v2/status" -ForegroundColor Cyan
try {
    $luminarStatus = Invoke-RestMethod -Uri "$baseUrl/api/luminar-nexus/v2/status" -Method Get -TimeoutSec 5
    Write-Host "[OK] Luminar routes working! Services: $($luminarStatus.total_services)" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Luminar routes not responding yet" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan; Write-Host "=".PadRight(68, "=") -ForegroundColor Cyan
Write-Host " NEXUS STARTUP COMPLETE" -ForegroundColor Cyan  
Write-Host "=" -NoNewline -ForegroundColor Cyan; Write-Host "=".PadRight(68, "=") -ForegroundColor Cyan
Write-Host ""
Write-Host "Access points:" -ForegroundColor White
Write-Host "  Frontend:       $baseUrl" -ForegroundColor Cyan
Write-Host "  Luminar Nexus:  $baseUrl/luminar-nexus" -ForegroundColor Cyan
Write-Host "  Memory Fabric:  $baseUrl/memory" -ForegroundColor Cyan
Write-Host "  API Status:     $baseUrl/api/luminar-nexus/v2/status" -ForegroundColor Cyan
Write-Host ""
Write-Host "[TIP] Press Ctrl+C to stop, then run: Stop-Process -Name node,python -Force" -ForegroundColor DarkGray
