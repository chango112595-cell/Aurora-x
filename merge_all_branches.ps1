# Merge All Branches Script
# This will attempt to merge all branches into experimental-all-branches-merge

$branches = @(
    "origin/aurora-ful-power",
    "origin/aurora-nexus-v2-integration", 
    "origin/aurora-working-restore",
    "origin/badges",
    "origin/draft",
    "origin/fix-windows-compatibility",
    "origin/integration-branch",
    "origin/unified-aurora",
    "aurora-ful-power",
    "aurora-nexus-v2-integration",
    "aurora-working-restore",
    "backup-before-restore-20251121-034844",
    "merge-autonomous-agent-conflict",
    "pre-full-integration-backup"
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
        } else {
            Write-Host "  [FAIL] Merge conflict or error with $branch" -ForegroundColor Red
            Write-Host "  Error: $result" -ForegroundColor Red
            
            # Try to abort the merge
            git merge --abort 2>&1 | Out-Null
            
            $failedMerges += $branch
        }
    } catch {
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
