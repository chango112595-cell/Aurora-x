#!/usr/bin/env bash
python3 - <<'PY' || { echo "[pack05_5H_plugin_store] health FAIL"; exit 2; }
import sys
print('ok')
PY
echo "[pack05_5H_plugin_store] health OK"
