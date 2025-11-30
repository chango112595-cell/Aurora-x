#!/usr/bin/env bash
python3 - <<'PY' || { echo "[pack05_5E_capability_system] health FAIL"; exit 2; }
import sys
print('ok')
PY
echo "[pack05_5E_capability_system] health OK"
