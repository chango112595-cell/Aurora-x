#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
MODE="${1:---dry-run}"
PY="${PYTHON:-python3}"

echo "[pack02] Installer invoked: mode=$MODE"

if [[ "$MODE" == "--dry-run" ]]; then
  echo "[pack02] Dry-run: running safe probe tests..."
  $PY "$ROOT/profiler/device_probe.py" --safe || { echo "[pack02] Dry-run failed"; exit 2; }
  $PY "$ROOT/profiler/export_profile.py" --dry || true
  echo "[pack02] Dry-run success."
  exit 0
fi

if [[ "$MODE" == "--install" ]]; then
  echo "[pack02] Performing install: creating logs and data"
  mkdir -p "$ROOT/logs" "$ROOT/data"
  echo "[pack02] Install: running safe probe and exporting profile."
  $PY "$ROOT/profiler/device_probe.py" --safe
  $PY "$ROOT/profiler/export_profile.py" --auto-deep --assume-no-interactive || true
  echo "[pack02] Install complete."
  exit 0
fi

echo "[pack02] unknown mode: $MODE"
exit 3
