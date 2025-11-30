#!/usr/bin/env bash
PIDS=$(pgrep -f "pack05_5L_test_framework" || true)
if [[ -n "$PIDS" ]]; then
  kill $PIDS || true
fi
