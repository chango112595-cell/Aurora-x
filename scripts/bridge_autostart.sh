#!/usr/bin/env bash
set -uo pipefail

echo "🔍 Checking Bridge service..."

BRIDGE_HOST="127.0.0.1"
BRIDGE_PORT="5001"
BRIDGE_URL="http://${BRIDGE_HOST}:${BRIDGE_PORT}/healthz"

# Check if Bridge is already running
if curl -fsS "${BRIDGE_URL}" >/dev/null 2>&1; then
    echo "✅ Bridge already running"
    exit 0
fi

# Kill any stale Bridge processes
pkill -f "aurora_x.bridge.service" 2>/dev/null || true
sleep 1

# Start Bridge in background
echo "🚀 Starting Aurora-X Factory Bridge..."
cd "$(dirname "$0")/.." || exit 1

# Start Bridge with output to log
python3 -m aurora_x.bridge.service >/tmp/bridge.log 2>&1 &
BRIDGE_PID=$!
echo $BRIDGE_PID > /tmp/bridge.pid
echo "📍 Bridge PID: $BRIDGE_PID"

# Wait for Bridge to be healthy (max 15 seconds)
echo "⏳ Waiting for Bridge to start..."
for i in {1..30}; do
    if curl -fsS "${BRIDGE_URL}" >/dev/null 2>&1; then
        echo "✅ Bridge healthy on port ${BRIDGE_PORT}"
        exit 0
    fi
    if ! kill -0 "${BRIDGE_PID}" >/dev/null 2>&1; then
        echo "❌ Bridge process exited early"
        break
    fi
    sleep 0.5
done

echo "⚠️  Bridge startup timeout"
if [ -f /tmp/bridge.log ]; then
    echo "📋 Bridge log output:"
    tail -n 30 /tmp/bridge.log
fi
echo "⚠️  Continuing anyway - Bridge may start in background"
exit 0
