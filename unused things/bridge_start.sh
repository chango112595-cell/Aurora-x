#!/bin/bash

echo "🚀 Starting Aurora-X Factory Bridge Service"
echo "=========================================="

# Kill any existing Bridge processes
pkill -f "bridge/service.py" 2>/dev/null
pkill -f "port=5001" 2>/dev/null

echo "Starting Bridge service on port 5001..."
cd /home/runner/workspace

# Start Bridge in background
nohup python3 aurora_x/bridge/service.py > /tmp/bridge.log 2>&1 &
BRIDGE_PID=$!

echo "Bridge started with PID: $BRIDGE_PID"
sleep 3

# Verify it's running
echo ""
echo "✅ Checking Bridge health:"
curl -s http://localhost:5001/healthz | python -m json.tool

echo ""
echo "Bridge service is ready!"