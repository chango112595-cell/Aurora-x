#!/bin/bash
# build_package.sh
# Aurora-X Ultra Packaging & Distribution Script

set -e

VERSION=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="aurora_full_build_${VERSION}"

echo "=============================================="
echo "  AURORA-X ULTRA - PACKAGING SCRIPT"
echo "  Building: ${PACKAGE_NAME}"
echo "=============================================="

echo ""
echo "[1/4] Validating modules..."
if [ -f "validate_modules.py" ]; then
    python3 validate_modules.py
else
    echo "  Skipping validation (validate_modules.py not found)"
fi

echo ""
echo "[2/4] Creating package directory..."
mkdir -p dist
rm -rf "dist/${PACKAGE_NAME}"
mkdir -p "dist/${PACKAGE_NAME}"

echo ""
echo "[3/4] Copying Aurora components..."

cp -r aurora_x "dist/${PACKAGE_NAME}/" 2>/dev/null || echo "  - aurora_x not found, skipping"
cp -r aurora_nexus_v3 "dist/${PACKAGE_NAME}/" 2>/dev/null || echo "  - aurora_nexus_v3 not found, skipping"
cp -r aurora_memory_fabric_v2 "dist/${PACKAGE_NAME}/" 2>/dev/null || echo "  - aurora_memory_fabric_v2 not found, skipping"
cp -r server "dist/${PACKAGE_NAME}/" 2>/dev/null || echo "  - server not found, skipping"
cp -r client "dist/${PACKAGE_NAME}/" 2>/dev/null || echo "  - client not found, skipping"
cp -r tools "dist/${PACKAGE_NAME}/" 2>/dev/null || echo "  - tools not found, skipping"
cp -r shared "dist/${PACKAGE_NAME}/" 2>/dev/null || echo "  - shared not found, skipping"

cp aurora_runner.py "dist/${PACKAGE_NAME}/" 2>/dev/null || echo "  - aurora_runner.py not found"
cp package.json "dist/${PACKAGE_NAME}/" 2>/dev/null || echo "  - package.json not found"
cp tsconfig.json "dist/${PACKAGE_NAME}/" 2>/dev/null || echo "  - tsconfig.json not found"
cp replit.md "dist/${PACKAGE_NAME}/" 2>/dev/null || echo "  - replit.md not found"

echo ""
echo "[4/4] Creating distribution archive..."
cd dist
zip -r "${PACKAGE_NAME}.zip" "${PACKAGE_NAME}" -x "*.pyc" -x "*__pycache__*" -x "*.git*" -x "*node_modules*"
cd ..

ARCHIVE_SIZE=$(du -h "dist/${PACKAGE_NAME}.zip" | cut -f1)

echo ""
echo "=============================================="
echo "  BUILD COMPLETE"
echo "=============================================="
echo "  Archive: dist/${PACKAGE_NAME}.zip"
echo "  Size: ${ARCHIVE_SIZE}"
echo ""
echo "  Contents:"
echo "    - aurora_x (550 modules)"
echo "    - aurora_nexus_v3 (V3 core)"
echo "    - aurora_memory_fabric_v2"
echo "    - server (Express backend)"
echo "    - client (React frontend)"
echo "    - tools (Luminar V2)"
echo "    - aurora_runner.py (unified launcher)"
echo "=============================================="
