#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
MODE="${1:---dry-run}"

echo "[pack01] Installer invoked: mode=$MODE"

if [[ "$MODE" == "--dry-run" ]]; then
  echo "[pack01] Dry-run: validating files and tests..."
  # Run unit tests quickly (non-destructive)
  if python3 -m pytest -q "$ROOT/tests" >/dev/null 2>&1; then
    echo "[pack01] Dry-run success: tests passed."
    exit 0
  else
    echo "[pack01] Dry-run failed: tests did not pass."
    exit 2
  fi
fi

if [[ "$MODE" == "--install" ]]; then
  echo "[pack01] Performing install steps..."
  # Create local state dir
  mkdir -p "$ROOT/logs" "$ROOT/data"
  echo "[pack01] Installation complete (non-destructive)."
  exit 0
fi

echo "[pack01] unknown mode: $MODE"
exit 3
