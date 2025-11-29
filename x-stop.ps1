Write-Host "🛑 Stopping all Aurora-X services..." -ForegroundColor Red

# find python and node processes belonging to aurora
$targets = @("server/index.ts", "aurora_nexus_v3", "luminar_nexus_v2", "aurora_core")

$procs = Get-Process | Where-Object {
    $_.Path -and ($_.Path -match "python" -or $_.Path -match "node")
}

foreach ($proc in $procs) {
    try {
        $cmdline = (Get-WmiObject Win32_Process -Filter "ProcessId=$($proc.Id)").CommandLine
        foreach ($t in $targets) {
            if ($cmdline -match $t) {
                Write-Host "🔻 Killing $($proc.ProcessName) ($($proc.Id))" -ForegroundColor Yellow
                Stop-Process -Id $proc.Id -Force
            }
        }
    } catch {}
}

Write-Host "✅ Aurora-X successfully stopped." -ForegroundColor Green
