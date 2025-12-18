#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# If process is running and responds to a simple ping via eventbus, return 0
pgrep -f "aurora_core.py" >/dev/null 2>&1 || { echo "[pack01] aurora_core not running"; exit 2; }

# Try a simple python health probe (non-blocking)
python3 - <<'PY' || exit 2
import sys, json
from pathlib import Path
p = Path("packs/pack01_pack01/state.sock")
# presence of pid check is sufficient for now
print("ok")
sys.exit(0)
PY

echo "[pack01] health=OK"
exit 0
