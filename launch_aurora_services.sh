#!/bin/bash
# Aurora-X Complete Service Launcher
# Starts all critical services and verifies they're online

echo "🚀 Aurora-X Service Launcher"
echo "======================================"
echo ""

# Function to start a service in background
start_service() {
    local name=$1
    local cmd=$2
    local port=$3
    
    echo "⚡ Starting $name (port $port)..."
    eval "$cmd" &
    local pid=$!
    echo "   PID: $pid"
    sleep 2
}

# Change to Aurora-X directory
cd /workspaces/Aurora-x

# Start services
echo "Starting services..."
echo ""

# 1. Python HTTP server for standalone dashboards (port 8000)
start_service "Standalone Dashboards Server" \
    "python -m http.server 8000 --directory /workspaces/Aurora-x" \
    "8000"

# 2. FastAPI/Learning Server (port 5002)
start_service "Learning API / FastAPI" \
    "python -m uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5002 --log-level error" \
    "5002"

# 3. Node.js Express Server (port 5000) - The main Aurora UI backend
echo "⚡ Starting Aurora UI Express Server (port 5000)..."
cd /workspaces/Aurora-x && npm run build 2>/dev/null || echo "Build skipped"
cd /workspaces/Aurora-x && node server.js &
local_pid=$!
echo "   PID: $local_pid"
sleep 3

echo ""
echo "======================================"
echo "✨ All services launched!"
echo "======================================"
echo ""

# Wait a moment then check status
sleep 2
python tools/check_services.py

echo ""
echo "🎯 Aurora UI available at: http://127.0.0.1:5000"
echo ""
