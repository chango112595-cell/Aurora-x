#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
# Stop aurora_core by looking at logs and process name
PIDS=$(pgrep -f "aurora_core.py" || true)
if [[ -z "$PIDS" ]]; then
  echo "[pack01] No aurora_core.py process found."
  exit 0
fi
echo "[pack01] Stopping aurora_core pids: $PIDS"
kill $PIDS || true
sleep 1
echo "[pack01] Stop issued."
