#!/usr/bin/env bash
set -euo pipefail
# best-effort stop for resident monitor processes
PIDS=$(pgrep -f "pack03_core.log" || true)
if [[ -n "$PIDS" ]]; then
  echo "[pack03] stopping pids: $PIDS"
  kill $PIDS || true
else
  echo "[pack03] no resident monitor found"
fi
