#!/usr/bin/env bash
PIDS=$(pgrep -f "pack05_5E_capability_system" || true)
if [[ -n "$PIDS" ]]; then
  kill $PIDS || true
fi
