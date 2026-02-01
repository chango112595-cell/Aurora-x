# BFG Purge .env.local from Git History
# Run this AFTER: 1) Rotating all secrets, 2) Disabling branch protection, 3) Installing Java
# Requires: Java (java -version), mirror clone, bfg.jar at C:\Users\negry\bfg.jar

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/chango112595-cell/Aurora-x.git"
$MirrorDir = "C:\Users\negry\aurora-x-mirror.git"
$BfgJar = "C:\Users\negry\bfg.jar"

Write-Host "=== BFG Purge .env.local ===" -ForegroundColor Cyan

# 0. Check Java
Write-Host "`n[0] Checking Java..." -ForegroundColor Yellow
try {
    $javaVersion = java -version 2>&1
    Write-Host $javaVersion
} catch {
    Write-Host "ERROR: Java not found. Install from https://adoptium.net/ or run: winget install EclipseAdoptium.Temurin.17.JDK" -ForegroundColor Red
    exit 1
}

# 1. Check bfg.jar exists
if (-not (Test-Path $BfgJar)) {
    Write-Host "ERROR: bfg.jar not found at $BfgJar" -ForegroundColor Red
    exit 1
}

# 2. Remove old mirror if exists, clone fresh mirror
Write-Host "`n[1] Creating mirror clone..." -ForegroundColor Yellow
if (Test-Path $MirrorDir) {
    Remove-Item -Recurse -Force $MirrorDir
}
Set-Location C:\Users\negry
git clone --mirror $RepoUrl aurora-x-mirror.git
if (-not (Test-Path $MirrorDir)) {
    Write-Host "ERROR: Mirror clone failed" -ForegroundColor Red
    exit 1
}

# 3. Run BFG to delete .env.local from all history
Write-Host "`n[2] Running BFG --delete-files .env.local ..." -ForegroundColor Yellow
Set-Location $MirrorDir
java -jar $BfgJar --delete-files .env.local .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: BFG failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

# 4. Expire reflog and garbage collect
Write-Host "`n[3] Expiring reflog and garbage collecting..." -ForegroundColor Yellow
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Verify .env.local is gone
Write-Host "`n[4] Verifying .env.local is gone from history..." -ForegroundColor Yellow
$logResult = git log --all -- .env.local 2>&1
if ($logResult) {
    Write-Host "WARNING: git log --all -- .env.local still returned output. Check manually." -ForegroundColor Yellow
    Write-Host $logResult
} else {
    Write-Host "PASS: git log --all -- .env.local returns nothing" -ForegroundColor Green
}

$revListResult = git rev-list --objects --all 2>&1 | Select-String -Pattern ".env.local" -SimpleMatch
if ($revListResult) {
    Write-Host "WARNING: .env.local still found in rev-list. Check manually." -ForegroundColor Yellow
} else {
    Write-Host "PASS: rev-list contains no .env.local" -ForegroundColor Green
}

# 6. Force push (user must have disabled branch protection)
Write-Host "`n[5] Force pushing rewritten history (--force --mirror)..." -ForegroundColor Yellow
Write-Host "    If this fails, disable branch protection in GitHub Settings -> Branches" -ForegroundColor Gray
git push --force --mirror
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: git push --force --mirror failed. Disable branch protection and retry." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== DONE ===" -ForegroundColor Green
Write-Host "Next steps:"
Write-Host "  1. Re-enable branch protection rules on GitHub"
Write-Host "  2. Notify team to re-clone or hard-reset (see TEAM_MESSAGE.txt)"
Write-Host "  3. Rotate any secrets that were not yet rotated"
