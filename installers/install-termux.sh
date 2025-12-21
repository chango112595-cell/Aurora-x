#!/usr/bin/env bash
set -euo pipefail
echo "Run inside Termux"

REPO_URL="${AURORA_REPO_URL:-https://github.com/chango112595-cell/Aurora-x}"
INSTALL_DIR="${AURORA_INSTALL_DIR:-$HOME/aurora-x}"

pkg update -y
pkg install -y python nodejs git
python -m pip install --upgrade pip
pip install -r requirements.txt || pip install fastapi uvicorn psutil watchdog websockets requests

if [ ! -d "$INSTALL_DIR" ]; then
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
chmod +x aurora-start aurora-stop || true
./aurora-start
