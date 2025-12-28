Write-Host "Starting Aurora-X full development environment..." -ForegroundColor Cyan

# Kill old ports (5000, 8000, 9000, 9100, 9200)
$ports = @(5000, 8000, 9000, 9100, 9200)
foreach ($port in $ports) {
    $p = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($p) {
        Write-Host "Port $port in use - terminating process $($p.OwningProcess)" -ForegroundColor Yellow
        Stop-Process -Id $p.OwningProcess -Force
    }
}

Write-Host "All required ports cleared." -ForegroundColor Green

# Open browser automatically after a short delay
Start-Job {
    Start-Sleep -Seconds 5
    Start-Process "http://localhost:5000"
} | Out-Null

npm run x-start
