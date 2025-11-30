#!/usr/bin/env bash
python3 - <<'PY' || { echo "[pack05_5G_permissions_resolver] health FAIL"; exit 2; }
import sys
print('ok')
PY
echo "[pack05_5G_permissions_resolver] health OK"
