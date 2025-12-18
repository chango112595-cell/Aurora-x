
Write-Host "`n=== AURORA SERVER DIAGNOSTIC REPORT ===`n" -ForegroundColor Cyan

# 1. Check all listening ports
Write-Host "▶ Checking Listening Ports..." -ForegroundColor Yellow
$ports = Get-NetTCPConnection -State Listen | Select-Object LocalPort,OwningProcess
$ports | Format-Table -AutoSize

# 2. Map PIDs to processes
Write-Host "`n▶ Mapping PIDs To Processes..." -ForegroundColor Yellow
foreach ($p in $ports) {
    try {
        $proc = Get-Process -Id $p.OwningProcess -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "Port $($p.LocalPort) → $($proc.ProcessName) (PID $($p.OwningProcess))"
        }
    } catch {}
}

# 3. Check if Node/Express Backend is Running
Write-Host "`n▶ Checking for Express Backend (port 5000)..." -ForegroundColor Yellow
$express = $ports | Where-Object { $_.LocalPort -eq 5000 }
if ($express) {
    Write-Host "✔ Express backend is RUNNING on port 5000" -ForegroundColor Green
} else {
    Write-Host "✘ Express backend NOT detected on port 5000" -ForegroundColor Red
}

# 4. Check for Python AI backend (port 8000 / 8100 / 9000)
$aiPorts = @(8000,8100,9000)
foreach ($p in $aiPorts) {
    Write-Host "`n▶ Checking AI backend port $p..." -ForegroundColor Yellow
    $check = $ports | Where-Object { $_.LocalPort -eq $p }
    if ($check) {
        Write-Host "✔ Python AI backend active on port $p" -ForegroundColor Green
    } else {
        Write-Host "✘ No AI backend detected on port $p" -ForegroundColor Red
    }
}

# 5. Check Node processes
Write-Host "`n▶ Checking Node.js Processes..." -ForegroundColor Yellow
Get-Process node -ErrorAction SilentlyContinue | Format-Table -AutoSize

# 6. Check Python processes
Write-Host "`n▶ Checking Python Processes..." -ForegroundColor Yellow
Get-Process python* -ErrorAction SilentlyContinue | Format-Table -AutoSize

Write-Host "`n=== END OF DIAGNOSTIC REPORT ===`n" -ForegroundColor Cyan
