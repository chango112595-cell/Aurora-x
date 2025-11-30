#!/usr/bin/env bash
set -euo pipefail
PIDS=$(pgrep -f "pack04_launcher/core/launcher.py" || true)
if [[ -n "$PIDS" ]]; then
  echo "[pack04] stopping pids: $PIDS"
  kill $PIDS || true
else
  echo "[pack04] no launcher process found"
fi
