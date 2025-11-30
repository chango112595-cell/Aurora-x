#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
python3 - <<'PY' || { echo "[pack04] health FAIL"; exit 2; }
import sys
sys.path.insert(0, "packs/pack04_launcher")
from core import supervisor, launcher
print("ok")
PY
echo "[pack04] health OK"
exit 0
