#!/usr/bin/env bash
set -e

echo "[Aurora Installer] Detecting system…"

OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

echo "OS: $OS"
echo "ARCH: $ARCH"

echo "[Aurora Installer] Installing dependencies…"

case "$OS" in
  linux)
    if command -v apt >/dev/null; then
      sudo apt update
      sudo apt install -y python3 python3-pip nodejs npm
    fi
    ;;
  darwin)
    brew install python node
    ;;
  *)
    echo "Unsupported OS."
    exit 1
    ;;
esac

echo "[Aurora Installer] Installing Aurora Python engine…"
pip3 install -r requirements.txt || true

echo "[Aurora Installer] Installing Node packages…"
npm install

echo "[Aurora Installer] Complete!"
