#!/usr/bin/env bash
set -euo pipefail
# Pull background jobs by name (simple best-effort)
PIDS=$(pgrep -f "export_profile.py" || true)
if [[ -n "$PIDS" ]]; then
  echo "[pack02] stopping profiler pids: $PIDS"
  kill $PIDS || true
else
  echo "[pack02] no profiler processes found"
fi
