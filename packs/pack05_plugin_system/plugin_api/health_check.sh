#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY' || { echo "[pack05] health FAIL"; exit 2; }
import sys
sys.path.insert(0, "packs/pack05_plugin_api")
from core.registry import PluginRegistry
pr = PluginRegistry()
print("ok")
PY
echo "[pack05] health OK"
exit 0
