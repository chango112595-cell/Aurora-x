#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
MODE="${1:---dry-run}"
PY="${PYTHON:-python3}"

echo "[pack04] Installer invoked: mode=$MODE"

if [[ "$MODE" == "--dry-run" ]]; then
  echo "[pack04] Dry-run: running unit tests"
  (cd "$ROOT" && python3 -m pytest -q tests) >/dev/null 2>&1 && echo "[pack04] Dry-run tests passed." || { echo "[pack04] Dry-run tests failed"; exit 2; }
  exit 0
fi

if [[ "$MODE" == "--install" ]]; then
  echo "[pack04] Installing pack04_launcher..."
  mkdir -p "$ROOT/logs" "$ROOT/data" "$ROOT/run"
  echo "[pack04] Install done (non-destructive)."
  exit 0
fi

echo "[pack04] Unknown mode: $MODE"
exit 3
