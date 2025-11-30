#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "[pack05_5H_plugin_store] install (stub)"
mkdir -p "$ROOT/logs" "$ROOT/data"
echo "installed" > "$ROOT/data/installed.txt"
