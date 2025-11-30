#!/usr/bin/env bash
python3 - <<'PY' || { echo "[pack05_5J_state_persistence] health FAIL"; exit 2; }
import sys
print('ok')
PY
echo "[pack05_5J_state_persistence] health OK"
