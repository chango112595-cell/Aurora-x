#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"

echo "[pack01] Starting Unified Process Core..."
# Run aurora_core.py in background, redirect logs to pack logs
mkdir -p "$ROOT/logs"
nohup $PY "$ROOT/aurora_core.py" >> "$ROOT/logs/aurora_core.log" 2>&1 &
sleep 1
echo "[pack01] aurora_core launched (pid: $!)"
