Param(
  [string]$BaseBranch = "vs-code-aurora-version",
  [string]$HeadBranch = "chore/ci-hygiene",
  [switch]$NoPr
)

function Fail($msg) { Write-Host "ERROR: $msg" -ForegroundColor Red; exit 1 }

# 0) Sanity: repo root
$inside = (git rev-parse --is-inside-work-tree) 2>$null
if ($LASTEXITCODE -ne 0) { Fail "Run this script from your repo root (folder with .git)" }

# 1) Ensure branch exists and is checked out
git fetch origin $BaseBranch | Out-Null
git checkout -B $HeadBranch origin/$BaseBranch

# 2) Make directories
New-Item -ItemType Directory -Force .github\workflows | Out-Null
New-Item -ItemType Directory -Force tests | Out-Null

# 3) Move proposed files into place
if (Test-Path .\proposed\.gitignore) { Move-Item -Force .\proposed\.gitignore .\.gitignore }
if (Test-Path .\proposed\.github\workflows\aurora-e2e.yml) { Move-Item -Force .\proposed\.github\workflows\aurora-e2e.yml .\.github\workflows\aurora-e2e.yml }
if (Test-Path .\proposed\tests\test_health.py) { Move-Item -Force .\proposed\tests\test_health.py .\tests\test_health.py }
if (Test-Path .\proposed\PR_BODY.md) { Move-Item -Force .\proposed\PR_BODY.md .\PR_BODY.md }

# 4) Stop tracking artifacts/secrets (keeps local files)
git rm -r --cached --ignore-unmatch .next .venv aurora_x.egg-info runs pack_zips backups attached_assets mcp_bundle_output project_export .ssl secrets .vscode 2>$null
git rm --cached --ignore-unmatch .env .env.local .env.* 2>$null

# 5) Commit & push
git add .gitignore .github\workflows\aurora-e2e.yml tests\test_health.py 2>$null
git commit -m "chore(ci,git): tighten E2E; ignore artifacts & secrets; add health test" || Write-Host "Nothing to commit, continuing..."
git push -u origin $HeadBranch

# 6) Create PR
if (-not $NoPr) {
  if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh pr create --base $BaseBranch --head $HeadBranch --title "chore(ci,git): tighten E2E; ignore artifacts/secrets; add health test" --body-file PR_BODY.md
  } else {
    $url = "https://github.com/chango112595-cell/Aurora-x/compare/{0}...{1}?quick_pull=1" -f $BaseBranch, $HeadBranch
    Write-Host "`nOpen this link to create the PR:" -ForegroundColor Yellow
    Write-Host $url
    try { Start-Process $url } catch {}
  }
}
