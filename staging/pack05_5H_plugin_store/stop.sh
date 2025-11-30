#!/usr/bin/env bash
PIDS=$(pgrep -f "pack05_5H_plugin_store" || true)
if [[ -n "$PIDS" ]]; then
  kill $PIDS || true
fi
