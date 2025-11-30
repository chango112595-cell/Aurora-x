#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Installing automotive dependencies..."
# Debian/Ubuntu example
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv can-utils
python3 -m venv "$ROOT/.venv_auto"
source "$ROOT/.venv_auto/bin/activate"
pip install --upgrade pip
pip install python-can udsoncan isotp
echo "Automotive runtime installed. Run: python3 automotive/can_bridge.py"
