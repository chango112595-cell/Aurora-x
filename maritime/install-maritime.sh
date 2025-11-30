#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv_maritime
source .venv_maritime/bin/activate
pip install pynmea2
echo "Maritime tools installed. Run maritime/nmea_bridge.py"
