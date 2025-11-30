#!/usr/bin/env bash
PIDS=$(pgrep -f "pack05_5J_state_persistence" || true)
if [[ -n "$PIDS" ]]; then
  kill $PIDS || true
fi
