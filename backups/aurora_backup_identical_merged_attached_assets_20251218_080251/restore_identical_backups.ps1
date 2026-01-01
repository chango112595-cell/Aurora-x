param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\.."))
)

$ErrorActionPreference = "Stop"
$archiveRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$manifestPath = Join-Path $archiveRoot "manifest.json"

if (!(Test-Path $manifestPath)) {
  throw "Missing manifest.json at $manifestPath"
}

$items = Get-Content $manifestPath -Raw | ConvertFrom-Json
$restored = 0
foreach ($item in $items) {
  $originalPath = Join-Path $RepoRoot $item.original
  $archivedPath = $item.archived

  if (Test-Path $originalPath) {
    Write-Host "SKIP (exists): $($item.original)"
    continue
  }

  $origDir = Split-Path $originalPath -Parent
  New-Item -ItemType Directory -Force -Path $origDir | Out-Null

  if (!(Test-Path $archivedPath)) {
    Write-Host "MISSING ARCHIVE: $archivedPath"
    continue
  }

  Move-Item -Path $archivedPath -Destination $originalPath
  Write-Host "RESTORED: $($item.original)"
  $restored++
}

Write-Host "Done. Restored $restored file(s)."
