# Check all Nexus systems status

Write-Host ""
Write-Host "AURORA NEXUS STATUS CHECK" -ForegroundColor Cyan
Write-Host "=" -NoNewline; Write-Host "=".PadRight(68, "=")
Write-Host ""

<<<<<<< HEAD
$auroraBaseUrl = $env:AURORA_BASE_URL
$auroraScheme = $env:AURORA_SCHEME
$auroraHost = $env:AURORA_HOST

if ($auroraBaseUrl) {
    try {
        $baseUri = [System.Uri]$auroraBaseUrl
        if (-not $auroraScheme) { $auroraScheme = $baseUri.Scheme }
        if (-not $auroraHost) { $auroraHost = $baseUri.Host }
    } catch {
        Write-Host "[WARN] Invalid AURORA_BASE_URL provided; falling back to host/scheme defaults." -ForegroundColor Yellow
        $auroraBaseUrl = $null
    }
}

if (-not $auroraScheme) { $auroraScheme = "http" }
if (-not $auroraHost) { $auroraHost = "127.0.0.1" }

$baseUrl = "$auroraScheme://$auroraHost"
$frontendBaseUrl = if ($auroraBaseUrl) { $auroraBaseUrl.TrimEnd("/") } else { "$baseUrl:5000" }
=======
$auroraHost = if ($env:AURORA_HOST) { $env:AURORA_HOST } else { "127.0.0.1" }
$baseUrl = if ($env:AURORA_BASE_URL) { $env:AURORA_BASE_URL } else { "http://$auroraHost:5000" }
$luminarUrl = if ($env:AURORA_LUMINAR_URL) { $env:AURORA_LUMINAR_URL } else { "http://$auroraHost:8000" }
>>>>>>> 49b60f0475b5dbe841523c9d5d27758717b03e99

# Check Luminar Nexus V2 Backend
Write-Host "[1] Luminar Nexus V2 (Direct - Port 8000)" -ForegroundColor Yellow
try {
<<<<<<< HEAD
    $nexusV2 = Invoke-RestMethod -Uri "$baseUrl:8000/api/nexus/status" -TimeoutSec 3
=======
    $nexusV2 = Invoke-RestMethod -Uri "$luminarUrl/api/nexus/status" -TimeoutSec 3
>>>>>>> 49b60f0475b5dbe841523c9d5d27758717b03e99
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
Write-Host "[2] Express Backend (Port 5000)" -ForegroundColor Yellow
try {
<<<<<<< HEAD
    $backend = Invoke-RestMethod -Uri "$frontendBaseUrl/api/health" -TimeoutSec 3
=======
    $backend = Invoke-RestMethod -Uri "$baseUrl/api/health" -TimeoutSec 3
>>>>>>> 49b60f0475b5dbe841523c9d5d27758717b03e99
    Write-Host "    Status: OK" -ForegroundColor Green
} catch {
    Write-Host "    Status: OFFLINE" -ForegroundColor Red
}

Write-Host ""

# Check Luminar Nexus Routes (through Express)
Write-Host "[3] Luminar Nexus Routes (via Express)" -ForegroundColor Yellow
try {
<<<<<<< HEAD
    $luminarProxy = Invoke-RestMethod -Uri "$frontendBaseUrl/api/luminar-nexus/v2/status" -TimeoutSec 3
=======
    $luminarProxy = Invoke-RestMethod -Uri "$baseUrl/api/luminar-nexus/v2/status" -TimeoutSec 3
>>>>>>> 49b60f0475b5dbe841523c9d5d27758717b03e99
    Write-Host "    Status: OK (Proxying to Luminar V2)" -ForegroundColor Green
    Write-Host "    Services: $($luminarProxy.total_services)" -ForegroundColor Gray
} catch {
    Write-Host "    Status: NOT AVAILABLE" -ForegroundColor Red
    Write-Host "    Note: Luminar V2 needs to be running on port 8000" -ForegroundColor Yellow
}

Write-Host ""

# Check Memory Fabric
Write-Host "[4] Memory Fabric Integration" -ForegroundColor Yellow
try {
<<<<<<< HEAD
    $memory = Invoke-RestMethod -Uri "$frontendBaseUrl/api/memory/status" -TimeoutSec 3
=======
    $memory = Invoke-RestMethod -Uri "$baseUrl/api/memory/status" -TimeoutSec 3
>>>>>>> 49b60f0475b5dbe841523c9d5d27758717b03e99
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
<<<<<<< HEAD
        $response = Invoke-WebRequest -Uri "$frontendBaseUrl$page" -TimeoutSec 2 -UseBasicParsing
=======
        $response = Invoke-WebRequest -Uri "$baseUrl$page" -TimeoutSec 2 -UseBasicParsing
>>>>>>> 49b60f0475b5dbe841523c9d5d27758717b03e99
        Write-Host "    $page - OK" -ForegroundColor Green
    } catch {
        Write-Host "    $page - ERROR" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" -NoNewline; Write-Host "=".PadRight(68, "=")
Write-Host ""
