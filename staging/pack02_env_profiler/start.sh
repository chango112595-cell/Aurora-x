#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"
echo "[pack02] Starting profiler service (one-shot run)..."
# profiler is usually run on-demand; starting will export current profile to live/environment
$PY "$ROOT/profiler/export_profile.py" --auto-deep --assume-no-interactive >> "$ROOT/logs/start.log" 2>&1 &
sleep 1
echo "[pack02] profiler launched (background)"
