#!/usr/bin/env bash
PIDS=$(pgrep -f "pack05_5G_permissions_resolver" || true)
if [[ -n "$PIDS" ]]; then
  kill $PIDS || true
fi
