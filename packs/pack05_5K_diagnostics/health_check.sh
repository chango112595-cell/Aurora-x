#!/usr/bin/env bash
python3 - <<'PY' || { echo "[pack05_5K_diagnostics] health FAIL"; exit 2; }
import sys
print('ok')
PY
echo "[pack05_5K_diagnostics] health OK"
