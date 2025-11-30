#!/usr/bin/env bash
python3 - <<'PY' || { echo "[pack05_5I_versioning_upgrades] health FAIL"; exit 2; }
import sys
print('ok')
PY
echo "[pack05_5I_versioning_upgrades] health OK"
