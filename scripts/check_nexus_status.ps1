# Check all Nexus systems status

Write-Host ""
Write-Host "AURORA NEXUS STATUS CHECK" -ForegroundColor Cyan
Write-Host "=" -NoNewline; Write-Host "=".PadRight(68, "=")
Write-Host ""

$auroraHost = if ($env:AURORA_HOST) { $env:AURORA_HOST } else { "127.0.0.1" }
$baseUrl = if ($env:AURORA_BASE_URL) { $env:AURORA_BASE_URL } else { "http://$auroraHost:5000" }
$luminarUrl = if ($env:AURORA_LUMINAR_URL) { $env:AURORA_LUMINAR_URL } else { "http://$auroraHost:8000" }

# Check Luminar Nexus V2 Backend
Write-Host "[1] Luminar Nexus V2 (Direct - Port $LuminarPort)" -ForegroundColor Yellow
try {
    $nexusV2 = Invoke-RestMethod -Uri "$luminarUrl/api/nexus/status" -TimeoutSec 3
    Write-Host "    Status: OK" -ForegroundColor Green
    Write-Host "    Version: $($nexusV2.version)" -ForegroundColor Gray
    Write-Host "    Services: $($nexusV2.total_services)" -ForegroundColor Gray
    Write-Host "    Healthy: $($nexusV2.healthy_services)" -ForegroundColor Gray
    Write-Host "    Quantum Coherence: $([math]::Round($nexusV2.quantum_coherence * 100, 1))%" -ForegroundColor Gray
}
catch {
    Write-Host "    Status: OFFLINE" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor DarkRed
}

Write-Host ""

# Check Express Backend Integration
Write-Host "[2] Express Backend (Port $AuroraPort)" -ForegroundColor Yellow
try {
    $backend = Invoke-RestMethod -Uri "$baseUrl/api/health" -TimeoutSec 3
    Write-Host "    Status: OK" -ForegroundColor Green
}
catch {
    Write-Host "    Status: OFFLINE" -ForegroundColor Red
}

Write-Host ""

# Check Luminar Nexus Routes (through Express)
Write-Host "[3] Luminar Nexus Routes (via Express)" -ForegroundColor Yellow
try {
    $luminarProxy = Invoke-RestMethod -Uri "$baseUrl/api/luminar-nexus/v2/status" -TimeoutSec 3
    Write-Host "    Status: OK (Proxying to Luminar V2)" -ForegroundColor Green
    Write-Host "    Services: $($luminarProxy.total_services)" -ForegroundColor Gray
}
catch {
    Write-Host "    Status: NOT AVAILABLE" -ForegroundColor Red
    Write-Host "    Note: Luminar V2 needs to be running on port $LuminarPort" -ForegroundColor Yellow
}

Write-Host ""

# Check Memory Fabric
Write-Host "[4] Memory Fabric Integration" -ForegroundColor Yellow
try {
    $memory = Invoke-RestMethod -Uri "$baseUrl/api/memory/status" -TimeoutSec 3
    Write-Host "    Status: OK" -ForegroundColor Green
    Write-Host "    Connected: $($memory.connected)" -ForegroundColor Gray
}
catch {
    Write-Host "    Status: OFFLINE" -ForegroundColor Red
}

Write-Host ""

# Check Frontend Access
Write-Host "[5] Frontend Pages" -ForegroundColor Yellow
$pages = @("/", "/memory", "/luminar-nexus", "/chat")
foreach ($page in $pages) {
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl$page" -TimeoutSec 2 -UseBasicParsing
        Write-Host "    $page - OK" -ForegroundColor Green
    }
    catch {
        Write-Host "    $page - ERROR" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" -NoNewline; Write-Host "=".PadRight(68, "=")
Write-Host ""
