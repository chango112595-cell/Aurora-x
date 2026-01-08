Param(
  [int[]]$PRs = @(177,178,179,180,181,710)
)

function Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Warn($m){ Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Has($n){ $null -ne (Get-Command $n -ErrorAction SilentlyContinue) }

if (-not (Has git)) { throw "git not found" }
if (-not (Has gh))  { throw "GitHub CLI 'gh' not found. Run: gh auth login" }

function Patch-Yaml($path){
  if (!(Test-Path $path)) { return $false }
  $y = Get-Content $path -Raw
  $orig = $y

  # Normalize bad PS-expanded token and prefer $HOST
  $y = $y -replace 'System\.Management\.Automation\.Internal\.Host\.InternalHost','HOST'
  $y = $y -replace 'http://127\.0\.0\.1:8000/healthz','"$HOST/healthz"'
  $y = $y -replace '(?<!")\$HOST/healthz(?!")','"$HOST/healthz"'

  # Bump timeout 30 -> 120 (idempotent)
  $y = $y -replace 'timeout\s+30','timeout 120'

  if ($y -ne $orig) {
    Set-Content -Encoding UTF8 $path $y
    git add $path | Out-Null
    return $true
  }
  return $false
}

foreach ($id in $PRs) {
  $branch = gh pr view $id --json headRefName --jq .headRefName 2>$null
  if (-not $branch) { Warn ("PR #{0}: can't resolve branch; skipping" -f $id); continue }

  Info ("Patching PR #{0} (branch: {1})…" -f $id, $branch)
  git fetch origin $branch | Out-Null
  git checkout -B $branch origin/$branch | Out-Null

  $changed = $false
  $changed = (Patch-Yaml ".github/workflows/aurora-e2e.yml") -or $changed
  $changed = (Patch-Yaml ".github/workflows/docker-e2e.yml") -or $changed

  if ($changed) {
    git commit -m "ci(e2e): use `$HOST/healthz and extend wait to 120s" | Out-Null
    git push -u origin $branch | Out-Null
    Info ("Pushed. Checks will rerun for PR #{0}." -f $id)
  } else {
    Warn ("PR #{0}: nothing to change" -f $id)
  }
}
