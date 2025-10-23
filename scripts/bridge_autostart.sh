#!/usr/bin/env bash
set -euo pipefail

# Check if Bridge is already running
if curl -fsS http://127.0.0.1:5001/healthz >/dev/null 2>&1; then
    echo "✅ Bridge already running"
    exit 0
fi

# Start Bridge in background
echo "🚀 Starting Aurora-X Factory Bridge..."
nohup python3 -m aurora_x.bridge.service >/tmp/bridge.log 2>&1 &
BRIDGE_PID=$!
echo $BRIDGE_PID > /tmp/bridge.pid

# Wait for Bridge to be healthy (max 10 seconds)
for i in {1..20}; do
    if curl -fsS http://127.0.0.1:5001/healthz >/dev/null 2>&1; then
        echo "✅ Bridge healthy on port 5001"
        exit 0
    fi
    sleep 0.5
done

echo "⚠️  Bridge startup timeout - check /tmp/bridge.log"
exit 1