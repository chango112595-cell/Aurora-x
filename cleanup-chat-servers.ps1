Get-NetTCPConnection -LocalPort 9000 -ErrorAction SilentlyContinue | ForEach-Object {
    $processId = $_.OwningProcess
    Write-Host \"Stopping chat server process $processId on port 9000...\"
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
}
Write-Host \"All chat servers on port 9000 stopped.\"
