# Kill all Aurora Node processes
# Usage: .\scripts\kill-aurora.ps1

Write-Host "🔍 Finding Aurora Node processes..." -ForegroundColor Cyan

$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue

if ($nodeProcesses) {
    Write-Host "Found $($nodeProcesses.Count) Node process(es):" -ForegroundColor Yellow
    $nodeProcesses | ForEach-Object {
        Write-Host "  PID: $($_.Id) | Started: $($_.StartTime)" -ForegroundColor Gray
    }

    Write-Host "`n🛑 Stopping all Node processes..." -ForegroundColor Yellow
    $nodeProcesses | Stop-Process -Force

    Start-Sleep -Seconds 2

    # Check if port 5000 is free
    $port5000 = netstat -ano | findstr :5000 | findstr LISTENING
    if ($port5000) {
        Write-Host "⚠️  Port 5000 is still in use!" -ForegroundColor Red
        Write-Host $port5000 -ForegroundColor Gray
    } else {
        Write-Host "✅ Port 5000 is now free" -ForegroundColor Green
    }

    Write-Host "`n✅ All Node processes stopped" -ForegroundColor Green
} else {
    Write-Host "✅ No Node processes found" -ForegroundColor Green
}
