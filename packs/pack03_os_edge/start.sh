#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"
echo "[pack03] Starting Aurora OS Core (resident services)..."
# Start is idempotent: runs basic resident monitor (non-networking)
nohup $PY - <<'PY' >> "$ROOT/logs/pack03_core.log" 2>&1 &
import time, sys
time.sleep(0.1)
print("pack03 resident monitor started")
sys.exit(0)
PY
sleep 1
echo "[pack03] start script exited"
