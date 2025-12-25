# Check all Nexus systems status

Write-Host ""
Write-Host "AURORA NEXUS STATUS CHECK" -ForegroundColor Cyan
Write-Host "=" -NoNewline; Write-Host "=".PadRight(68, "=")
Write-Host ""

$AuroraHost = if ($env:AURORA_HOST) { $env:AURORA_HOST } else { "localhost" }
$AuroraPort = if ($env:AURORA_PORT) { $env:AURORA_PORT } else { "5000" }
$LuminarHost = if ($env:LUMINAR_HOST) { $env:LUMINAR_HOST } else { $AuroraHost }
$LuminarPort = if ($env:LUMINAR_PORT) { $env:LUMINAR_PORT } else { "8000" }

# Check Luminar Nexus V2 Backend
Write-Host "[1] Luminar Nexus V2 (Direct - Port $LuminarPort)" -ForegroundColor Yellow
try {
    $nexusV2 = Invoke-RestMethod -Uri "http://$LuminarHost`:$LuminarPort/api/nexus/status" -TimeoutSec 3
    Write-Host "    Status: OK" -ForegroundColor Green
    Write-Host "    Version: $($nexusV2.version)" -ForegroundColor Gray
    Write-Host "    Services: $($nexusV2.total_services)" -ForegroundColor Gray
    Write-Host "    Healthy: $($nexusV2.healthy_services)" -ForegroundColor Gray
    Write-Host "    Quantum Coherence: $([math]::Round($nexusV2.quantum_coherence * 100, 1))%" -ForegroundColor Gray
} catch {
    Write-Host "    Status: OFFLINE" -ForegroundColor Red
    Write-Host "    Error: $($_.Exception.Message)" -ForegroundColor DarkRed
}

Write-Host ""

# Check Express Backend Integration
Write-Host "[2] Express Backend (Port $AuroraPort)" -ForegroundColor Yellow
try {
    $backend = Invoke-RestMethod -Uri "http://$AuroraHost`:$AuroraPort/api/health" -TimeoutSec 3
    Write-Host "    Status: OK" -ForegroundColor Green
} catch {
    Write-Host "    Status: OFFLINE" -ForegroundColor Red
}

Write-Host ""

# Check Luminar Nexus Routes (through Express)
Write-Host "[3] Luminar Nexus Routes (via Express)" -ForegroundColor Yellow
try {
    $luminarProxy = Invoke-RestMethod -Uri "http://$AuroraHost`:$AuroraPort/api/luminar-nexus/v2/status" -TimeoutSec 3
    Write-Host "    Status: OK (Proxying to Luminar V2)" -ForegroundColor Green
    Write-Host "    Services: $($luminarProxy.total_services)" -ForegroundColor Gray
} catch {
    Write-Host "    Status: NOT AVAILABLE" -ForegroundColor Red
    Write-Host "    Note: Luminar V2 needs to be running on port $LuminarPort" -ForegroundColor Yellow
}

Write-Host ""

# Check Memory Fabric
Write-Host "[4] Memory Fabric Integration" -ForegroundColor Yellow
try {
    $memory = Invoke-RestMethod -Uri "http://$AuroraHost`:$AuroraPort/api/memory/status" -TimeoutSec 3
    Write-Host "    Status: OK" -ForegroundColor Green
    Write-Host "    Connected: $($memory.connected)" -ForegroundColor Gray
} catch {
    Write-Host "    Status: OFFLINE" -ForegroundColor Red
}

Write-Host ""

# Check Frontend Access
Write-Host "[5] Frontend Pages" -ForegroundColor Yellow
$pages = @("/", "/memory", "/luminar-nexus", "/chat")
foreach ($page in $pages) {
    try {
        $response = Invoke-WebRequest -Uri "http://$AuroraHost`:$AuroraPort$page" -TimeoutSec 2 -UseBasicParsing
        Write-Host "    $page - OK" -ForegroundColor Green
    } catch {
        Write-Host "    $page - ERROR" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" -NoNewline; Write-Host "=".PadRight(68, "=")
Write-Host ""
