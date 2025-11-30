#!/usr/bin/env bash
PIDS=$(pgrep -f "pack05_5K_diagnostics" || true)
if [[ -n "$PIDS" ]]; then
  kill $PIDS || true
fi
