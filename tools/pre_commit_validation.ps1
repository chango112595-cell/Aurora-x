# Pre-commit validation script for Aurora-X (PowerShell)
# Runs all validation checks before allowing commit

$ErrorActionPreference = "Stop"

Write-Host "🔍 Running Aurora-X pre-commit validation..." -ForegroundColor Cyan

# Set PYTHONPATH
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"

# 1. Syntax validation
Write-Host ""
Write-Host "1️⃣  Checking syntax..." -ForegroundColor Yellow
python tools/validate_syntax.py aurora_x/synthesis/universal_engine.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Syntax validation failed" -ForegroundColor Red
    exit 1
}

# 2. Endpoint validation
Write-Host ""
Write-Host "2️⃣  Checking endpoints..." -ForegroundColor Yellow
python tools/validate_endpoints.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Endpoint validation failed" -ForegroundColor Red
    exit 1
}

# 3. Service startup validation
Write-Host ""
Write-Host "3️⃣  Checking service startup..." -ForegroundColor Yellow
python tools/validate_service_startup.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Service startup validation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ All validation checks passed!" -ForegroundColor Green
