#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
echo "Integrating Pack6+7 into repo (dev mode)"
# add PYTHONPATH export for dev
grep -q "export PYTHONPATH" ~/.bashrc || echo "export PYTHONPATH=\$PYTHONPATH:$ROOT" >> ~/.bashrc
echo "Ensure you installed dependencies: pip install networkx psutil pytest"
echo "Start services for dev:"
echo "1) python3 aurora_os.py"
echo "2) python3 integration/dashboard/backend.py"
echo "3) python3 -m aurora_fw.builder.packager  (pack and then stage)"
echo ""
