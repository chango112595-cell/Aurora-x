#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOKEN="${1:-aurora-dev-token}"

echo "Aurora macOS installer"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Install python3 (brew install python) then re-run"
  exit 1
fi

python3 -m venv "$ROOT/.venv"
source "$ROOT/.venv/bin/activate"
pip install --upgrade pip
pip install fastapi uvicorn[standard] psutil watchdog websockets

if command -v npm >/dev/null 2>&1; then
  npm ci --prefix "$ROOT" || true
  npm i -g tsx || true
fi

mkdir -p "$ROOT/aurora_logs" "$ROOT/.aurora/pids"
echo "$TOKEN" > "$ROOT/.aurora/api.token"

echo "To install launchd plist (edit paths first):"
echo " cp packaging/aurora.plist ~/Library/LaunchAgents/"
echo " launchctl load ~/Library/LaunchAgents/com.aurora.os.plist"
echo "Start with: ./aurora.sh start"
