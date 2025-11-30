#!/usr/bin/env bash
pkg update -y
pkg install -y python nodejs git
python -m pip install --upgrade pip
pip install fastapi uvicorn psutil watchdog requests
git clone <your-repo> aurora
cd aurora
./aurora.sh start
