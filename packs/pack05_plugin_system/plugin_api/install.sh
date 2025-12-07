#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
MODE="${1:---dry-run}"
PY="${PYTHON:-python3}"

echo "[pack05] Installer invoked: mode=$MODE"

if [[ "$MODE" == "--dry-run" ]]; then
  echo "[pack05] Dry-run: running unit tests"
  (cd "$ROOT" && python3 -m pytest -q tests) >/dev/null 2>&1 && echo "[pack05] Dry-run tests passed." || { echo "[pack05] Dry-run tests failed"; exit 2; }
  exit 0
fi

if [[ "$MODE" == "--install" ]]; then
  echo "[pack05] Installing pack05_plugin_api..."
  mkdir -p "$ROOT/logs" "$ROOT/data" "$ROOT/data/plugins"
  echo "[pack05] Install done."
  exit 0
fi

echo "[pack05] Unknown mode: $MODE"
exit 3
