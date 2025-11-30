#!/usr/bin/env bash
set -euo pipefail
echo "Verifying environment..."
which python3 || (echo "python3 missing"; exit 1)
python3 -c "import sys, pkgutil; print('psutil', bool(pkgutil.find_loader('psutil'))); print('websockets', bool(pkgutil.find_loader('websockets')))"
which docker || echo "docker not found (optional)"
which npm || echo "npm not found (optional)"
echo "Done"
