#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE_USER="${1:-$USER}"
API_TOKEN="${2:-aurora-dev-token}"
MODE="${3:-systemd}" # systemd or none

echo "Aurora Native Linux installer"
echo "ROOT=$ROOT USER=$SERVICE_USER MODE=$MODE"

# ensure python
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 required; install it via apt/yum/pacman"
  exit 1
fi

# venv
python3 -m venv "$ROOT/.venv"
source "$ROOT/.venv/bin/activate"
pip install --upgrade pip
pip install fastapi uvicorn[standard] psutil watchdog websockets

# node (optional)
if command -v npm >/dev/null 2>&1; then
  echo "Installing node deps"
  npm ci --prefix "$ROOT" || true
  if ! command -v tsx >/dev/null 2>&1; then
    npm i -g tsx || true
  fi
fi

mkdir -p "$ROOT/aurora_logs" "$ROOT/.aurora/pids"
echo "$API_TOKEN" > "$ROOT/.aurora/api.token"

if [[ "$MODE" == "systemd" ]]; then
  echo "Installing systemd unit (packaging/aurora.service)"
  sudo cp "$ROOT/packaging/aurora.service" /etc/systemd/system/aurora.service
  sudo sed -i "s|/home/YOUR_USER/Aurora-x|$ROOT|g" /etc/systemd/system/aurora.service || true
  sudo systemctl daemon-reload
  sudo systemctl enable --now aurora.service
  echo "systemd service enabled"
fi

echo "Install complete. Run: $ROOT/aurora.sh start"
