#!/bin/bash
# Pre-commit validation script for Aurora-X
# Runs all validation checks before allowing commit

set -e

echo "🔍 Running Aurora-X pre-commit validation..."

# Set PYTHONPATH
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# 1. Syntax validation
echo ""
echo "1️⃣  Checking syntax..."
python tools/validate_syntax.py aurora_x/synthesis/universal_engine.py || {
    echo "❌ Syntax validation failed"
    exit 1
}

# 2. Endpoint validation
echo ""
echo "2️⃣  Checking endpoints..."
python tools/validate_endpoints.py || {
    echo "❌ Endpoint validation failed"
    exit 1
}

# 3. Service startup validation
echo ""
echo "3️⃣  Checking service startup..."
python tools/validate_service_startup.py || {
    echo "❌ Service startup validation failed"
    exit 1
}

echo ""
echo "✅ All validation checks passed!"
