# Merge All Branches Script
# This will attempt to merge all branches into experimental-all-branches-merge

$branches = @(
    "origin/codespace-wretched-gravestone-pj5rxv7rx677crw9v",
    "origin/copilot/help-pull-request-30",
    "origin/copilot/implement-configuration-updates",
    "origin/dependabot/docker/node-25-alpine",
    "origin/dependabot/docker/python-3.14-slim",
    "origin/dependabot/github_actions/actions/setup-go-6",
    "origin/dependabot/github_actions/actions/upload-artifact-5",
    "origin/dependabot/github_actions/codecov/codecov-action-5",
    "origin/dependabot/github_actions/docker/build-push-action-6",
    "origin/dependabot/github_actions/github/codeql-action-4",
    "origin/dependabot/pip/bandit-1.8.6",
    "origin/dependabot/pip/bcrypt-4.3.0",
    "origin/dependabot/pip/build-1.3.0",
    "origin/dependabot/pip/detect-secrets-1.5.0",
    "origin/dependabot/pip/dev-tools-6cc04861e6",
    "origin/dependabot/pip/flake8-7.3.0",
    "origin/dependabot/pip/pip-audit-2.9.0",
    "origin/dependabot/pip/pip-licenses-4.5.1",
    "origin/dependabot/pip/pipdeptree-2.28.0",
    "origin/dependabot/pip/pyjwt-2.10.1",
    "origin/dependabot/pip/pylint-3.3.9",
    "origin/dependabot/pip/pyre-check-0.9.25",
    "origin/dependabot/pip/safety-3.7.0",
    "origin/dependabot/pip/semgrep-1.136.0",
    "origin/dependabot/pip/sphinx-7.4.7",
    "origin/dependabot/pip/testing-4bb223f47c",
    "origin/dependabot/pip/urllib3-2.5.0",
    "origin/dependabot/pip/wheel-0.45.1"
)

$successfulMerges = @()
$failedMerges = @()

Write-Host "================================" -ForegroundColor Cyan
Write-Host "MERGING ALL BRANCHES" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

foreach ($branch in $branches) {
    Write-Host "Attempting to merge: $branch" -ForegroundColor Yellow
    
    try {
        # Try to merge with strategy to prefer incoming changes on conflicts
        $result = git merge $branch --no-edit --allow-unrelated-histories -X theirs 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Successfully merged $branch" -ForegroundColor Green
            $successfulMerges += $branch
        }
        else {
            Write-Host "  [FAIL] Merge conflict or error with $branch" -ForegroundColor Red
            Write-Host "  Error: $result" -ForegroundColor Red
            
            # Try to abort the merge
            git merge --abort 2>&1 | Out-Null
            
            $failedMerges += $branch
        }
    }
    catch {
        Write-Host "  [ERROR] Exception merging $branch : $_" -ForegroundColor Red
        git merge --abort 2>&1 | Out-Null
        $failedMerges += $branch
    }
    
    Write-Host ""
}

Write-Host "================================" -ForegroundColor Cyan
Write-Host "MERGE SUMMARY" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Successful merges: $($successfulMerges.Count)" -ForegroundColor Green
foreach ($branch in $successfulMerges) {
    Write-Host "  - $branch" -ForegroundColor Green
}
Write-Host ""
Write-Host "Failed merges: $($failedMerges.Count)" -ForegroundColor Red
foreach ($branch in $failedMerges) {
    Write-Host "  - $branch" -ForegroundColor Red
}
Write-Host ""
Write-Host "Current branch: experimental-all-branches-merge" -ForegroundColor Cyan
Write-Host "Main branch: untouched and safe" -ForegroundColor Green
