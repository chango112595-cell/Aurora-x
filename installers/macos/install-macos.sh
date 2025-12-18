#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="${HOME}/Aurora-x"

echo "Copying files to ${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}"
rsync -av --exclude '.git' "${ROOT}/" "${INSTALL_DIR}/"

cd "${INSTALL_DIR}"

# python venv
if ! command -v python3 >/dev/null 2>&1; then
  echo "Install Python 3 (from homebrew or python.org)"
  exit 1
fi

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" psutil watchdog requests

# optional: install node/npm if present
if command -v npm >/dev/null 2>&1; then
  npm install
  npm i -g tsx || true
fi

mkdir -p aurora_logs .aurora/pids
echo "aurora-dev-token" > ./.aurora/api.token

# create launchd plist for user-level auto-start
PLIST=~/Library/LaunchAgents/com.aurora.os.plist
cat > "${PLIST}" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" ...>
<plist version="1.0">
  <dict>
    <key>Label</key><string>com.aurora.os</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>${INSTALL_DIR}/aurora_os.py</string>
      <string>start</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>WorkingDirectory</key><string>${INSTALL_DIR}</string>
    <key>StandardOutPath</key><string>${INSTALL_DIR}/aurora_logs/launchd.out.log</string>
    <key>StandardErrorPath</key><string>${INSTALL_DIR}/aurora_logs/launchd.err.log</string>
  </dict>
</plist>
PL

echo "LaunchAgent created at ${PLIST}. Load it with: launchctl load ${PLIST}"
echo "macOS install complete."
