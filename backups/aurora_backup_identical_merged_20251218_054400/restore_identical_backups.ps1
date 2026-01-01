# Auto-generated restore script for identical .aurora_backup consolidation
$ErrorActionPreference = "Stop"
$archiveRoot = Resolve-Path "backups/aurora_backup_identical_merged_20251218_054400"

foreach ($item in Get-Content -Raw "$archiveRoot\manifest.json" | ConvertFrom-Json | Select-Object -ExpandProperty moved) {
  $src = Join-Path $archiveRoot $item.backup
  $dst = $item.backup
  $dstDir = Split-Path -Parent $dst
  if (!(Test-Path $src)) { continue }
  if (!(Test-Path $dstDir)) { New-Item -ItemType Directory -Force -Path $dstDir | Out-Null }
  if (Test-Path $dst) { throw "Restore would overwrite existing file: $dst" }
  Move-Item -Force -Path $src -Destination $dst
}
