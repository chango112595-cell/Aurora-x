# Aurora-X Release Script (PowerShell)
# Automates version tagging and release creation

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,

    [Parameter(Mandatory=$false)]
    [string]$Message = ""
)

# Validate version format (semver)
if ($Version -notmatch '^v\d+\.\d+\.\d+$') {
    Write-Host "Error: Version must follow semver format (e.g., v0.1.1)" -ForegroundColor Red
    exit 1
}

# Default message if not provided
if ([string]::IsNullOrEmpty($Message)) {
    $Message = "Aurora X $Version - $(Get-Date -Format 'yyyy-MM-dd')"
}

Write-Host "🚀 Creating release $Version..." -ForegroundColor Cyan
Write-Host "Message: $Message"
Write-Host ""

# Ensure we're on main and up to date
git checkout main
git pull origin main

# Check if tag already exists
$tagExists = git rev-parse "$Version" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Error: Tag $Version already exists" -ForegroundColor Red
    exit 1
}

# Create and push tag
Write-Host "📝 Creating tag..." -ForegroundColor Yellow
git tag -a "$Version" -m "$Message"
git push origin "$Version"

Write-Host ""
Write-Host "✅ Tag $Version pushed successfully" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Docker image will be built automatically:" -ForegroundColor Cyan
Write-Host "   ghcr.io/chango112595-cell/Aurora-x:$Version"
Write-Host ""
Write-Host "🔍 Verify workflow:" -ForegroundColor Cyan
Write-Host "   gh run list --workflow 'docker-release.yml' --limit 1"
Write-Host ""
Write-Host "📋 Check release:" -ForegroundColor Cyan
Write-Host "   gh release view $Version"
Write-Host ""
