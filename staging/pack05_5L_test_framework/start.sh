#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
nohup python3 - <<'PY' >> "$ROOT/logs/pack.log" 2>&1 &
import time, sys
time.sleep(0.1)
print("pack05_5L_test_framework started")
sys.exit(0)
PY
