#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"
nohup $PY "$ROOT/loader/sandbox_host.py" >> "$ROOT/logs/host.log" 2>&1 &
sleep 1
echo "[pack05-loader] host started"
