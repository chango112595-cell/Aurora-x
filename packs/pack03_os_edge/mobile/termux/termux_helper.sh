#!/usr/bin/env bash
echo "Termux helper: installs Python runtime and starts local aurora agent"
pkg update -y
pkg install -y python nodejs git
python -m pip install --upgrade pip
pip install requests websockets
git clone <your-repo> aurora || true
cd aurora
./aurora.sh start
