#!/usr/bin/env bash
python3 - <<'PY' || { echo "[pack05_5L_test_framework] health FAIL"; exit 2; }
import sys
print('ok')
PY
echo "[pack05_5L_test_framework] health OK"
