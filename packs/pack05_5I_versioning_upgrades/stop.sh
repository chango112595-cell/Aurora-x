#!/usr/bin/env bash
PIDS=$(pgrep -f "pack05_5I_versioning_upgrades" || true)
if [[ -n "$PIDS" ]]; then
  kill $PIDS || true
fi
