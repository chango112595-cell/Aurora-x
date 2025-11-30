#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"
echo "[pack04] Starting launcher supervisor..."
mkdir -p "$ROOT/logs"
nohup $PY "$ROOT/core/launcher.py" run >> "$ROOT/logs/launcher.log" 2>&1 &
sleep 1
echo "[pack04] launcher started"
