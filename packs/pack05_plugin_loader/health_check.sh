#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY' || { echo "[pack05-loader] health FAIL"; exit 2; }
import sys
sys.path.insert(0, "packs/pack05_plugin_loader")
from loader.sandbox_runtime import SandboxRuntime
r = SandboxRuntime("healthchk")
print("ok")
PY
echo "[pack05-loader] health OK"
exit 0
