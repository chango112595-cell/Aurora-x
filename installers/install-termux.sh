#!/usr/bin/env bash
set -euo pipefail
echo "Run inside Termux"
pkg update -y
pkg install -y python nodejs git
python -m pip install --upgrade pip
pip install fastapi uvicorn psutil watchdog websockets requests
git clone https://github.com/your/repo aurora || true
cd aurora
./aurora.sh start
