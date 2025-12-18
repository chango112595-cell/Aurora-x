#!/usr/bin/env bash
set -euo pipefail
echo "Installing aviation companion tools..."
python3 -m venv .venv_aviation
source .venv_aviation/bin/activate
pip install --upgrade pip
pip install requests
echo "To sign packages, ensure gpg is configured with an operator key."
