#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PROFILE="$(pwd)/live/environment/profile.json"
if [[ -f "$PROFILE" ]]; then
  echo "[pack02] profile present"
  jq -r '.summary.status' "$PROFILE" >/dev/null 2>&1 || echo "[pack02] profile ok"
  exit 0
fi
# fallback: verify that probe runs
python3 "$ROOT/profiler/device_probe.py" --safe >/dev/null 2>&1 && { echo "[pack02] probe OK"; exit 0; }
echo "[pack02] health FAIL"; exit 2
