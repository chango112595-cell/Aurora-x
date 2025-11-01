#!/bin/bash
# Quick Aurora status check and startup
cd /workspaces/Aurora-x

echo "🔍 Checking Aurora services..."
python tools/check_services.py

echo ""
echo "Starting any missing services..."
echo ""

# Check each port and start if needed
check_and_start() {
    local port=$1
    local name=$2
    local cmd=$3
    
    if ! python -c "import socket; s=socket.socket(); s.settimeout(1); result=s.connect_ex(('127.0.0.1',$port)); s.close(); exit(0 if result==0 else 1)" 2>/dev/null; then
        echo "Starting $name (port $port)..."
        eval "$cmd &"
        sleep 2
    fi
}

# Start port 8000 (dashboards)
check_and_start 8000 "Dashboard Server" "python -m http.server 8000 --directory /workspaces/Aurora-x 2>/dev/null"

# Start port 5002 (FastAPI)
check_and_start 5002 "Learning API" "python -m uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5002 --log-level error 2>/dev/null"

# Start port 5000 (Express)
check_and_start 5000 "Aurora UI Express" "cd /workspaces/Aurora-x && node server.js 2>/dev/null"

echo ""
sleep 2
echo "Final status check:"
python tools/check_services.py
