Param(
  [int[]]$PRs = @(177,178,179,180,181)   # add more PR numbers if you want
)

function Info { param($m) Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Warn { param($m) Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Has  { param($n) $null -ne (Get-Command $n -ErrorAction SilentlyContinue) }

if (-not (Has git)) { throw "git not found" }
if (-not (Has gh))  { throw "GitHub CLI 'gh' not found. Run: gh auth login" }

$starting = (git rev-parse --abbrev-ref HEAD) 2>$null

foreach ($id in $PRs) {
  $branch = gh pr view $id --json headRefName --jq .headRefName 2>$null
  if (-not $branch) { Warn ("PR #{0}: can't resolve branch; skipping" -f $id); continue }

  Info ("Re-triggering checks for PR #{0} (branch: {1})…" -f $id, $branch)
  git fetch origin $branch | Out-Null
  git checkout -B $branch origin/$branch | Out-Null
  git commit --allow-empty -m "ci: retrigger checks" --no-verify | Out-Null
  git push -u origin $branch | Out-Null
}

if ($starting) { git checkout $starting | Out-Null }
