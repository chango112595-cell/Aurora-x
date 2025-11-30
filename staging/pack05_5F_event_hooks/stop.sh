#!/usr/bin/env bash
PIDS=$(pgrep -f "pack05_5F_event_hooks" || true)
if [[ -n "$PIDS" ]]; then
  kill $PIDS || true
fi
