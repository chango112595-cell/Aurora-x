#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="/opt/auroraos"
TOKEN="${1:-aurora-dev-token}"

sudo mkdir -p "$INSTALL_DIR"
sudo rsync -av --exclude='.git' "$ROOT/" "$INSTALL_DIR/"

sudo chown -R $(id -u):$(id -g) "$INSTALL_DIR"

python3 -m venv "$INSTALL_DIR/.venv"
source "$INSTALL_DIR/.venv/bin/activate"
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" psutil watchdog requests

if command -v npm >/dev/null 2>&1; then
  cd "$INSTALL_DIR"
  npm install || true
  npm i -g tsx || true
fi

mkdir -p "$INSTALL_DIR/aurora_logs" "$INSTALL_DIR/.aurora/pids"
echo "$TOKEN" > "$INSTALL_DIR/.aurora/api.token"

# systemd unit
sudo cp "$ROOT/packaging/aurora.service" /etc/systemd/system/aurora.service
sudo sed -i "s|/home/YOUR_USER/Aurora-x|$INSTALL_DIR|g" /etc/systemd/system/aurora.service || true
sudo systemctl daemon-reload
sudo systemctl enable --now aurora.service

echo "Native install complete. Service registered as 'aurora'."
