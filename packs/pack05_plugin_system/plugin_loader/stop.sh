#!/usr/bin/env bash
set -euo pipefail
PIDS=$(pgrep -f "loader/sandbox_host.py" || true)
if [[ -n "$PIDS" ]]; then
  kill $PIDS || true
  echo "[pack05-loader] host stopped"
else
  echo "[pack05-loader] no host found"
fi
