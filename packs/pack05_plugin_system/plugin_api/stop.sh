#!/usr/bin/env bash
set -euo pipefail
PIDS=$(pgrep -f "core/loader.py" || true)
if [[ -n "$PIDS" ]]; then
  kill $PIDS || true
  echo "[pack05] loader stopped"
else
  echo "[pack05] no loader process"
fi
