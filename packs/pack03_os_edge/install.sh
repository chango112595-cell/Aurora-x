#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
MODE="${1:---dry-run}"
PY="${PYTHON:-python3}"

echo "[pack03] Installer invoked: mode=$MODE"

if [[ "$MODE" == "--dry-run" ]]; then
  echo "[pack03] Dry-run: running unit tests"
  (cd "$ROOT" && python3 -m pytest -q tests) >/dev/null 2>&1 && echo "[pack03] Dry-run tests passed." || { echo "[pack03] Dry-run tests failed"; exit 2; }
  exit 0
fi

if [[ "$MODE" == "--install" ]]; then
  echo "[pack03] Installing pack03_os_base..."
  mkdir -p "$ROOT/logs" "$ROOT/data"
  echo "[pack03] Install done (non-destructive)."
  exit 0
fi

echo "[pack03] Unknown mode: $MODE"
exit 3
