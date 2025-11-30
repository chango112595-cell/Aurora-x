#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# basic health: run a small import test of core modules
python3 - <<'PY' || { echo "[pack03] health FAIL"; exit 2; }
import sys
sys.path.insert(0, "packs/pack03_os_base")
from core import vfs, namespace, scheduler, process_abstraction
print("ok")
PY
echo "[pack03] health OK"
exit 0
