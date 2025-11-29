#!/bin/bash
# Aurora-X Bootstrap Script
# Starts all required services for the Chango platform

echo "🌌 Aurora-X Bootstrap Starting..."
echo ""

# Kill any existing processes on required ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:5000,5001,5002,5003 | xargs kill -9 2>/dev/null || true
sleep 2

# Start Python Bridge Service (Port 5001)
echo "🌉 Starting Bridge Service on port 5001..."
python3 -m aurora_x.bridge.service &
BRIDGE_PID=$!
echo "   PID: $BRIDGE_PID"
sleep 2

# Start Python Self-Learning Server (Port 5002)
echo "🧠 Starting Self-Learning Server on port 5002..."
python3 -m aurora_x.self_learn_server &
SELFLEARN_PID=$!
echo "   PID: $SELFLEARN_PID"
sleep 2

# Start Python Chat Server (Port 5003)
echo "💬 Starting Chat Server on port 5003..."
python3 -c 'from tools.luminar_nexus import run_chat_server; run_chat_server(5003)' &
CHAT_PID=$!
echo "   PID: $CHAT_PID"
sleep 3

# Check if Python services are responding
echo ""
echo "🔍 Checking service health..."
for port in 5001 5002 5003; do
    if lsof -i:$port > /dev/null 2>&1; then
        echo "   ✅ Port $port is active"
    else
        echo "   ⚠️  Port $port not responding"
    fi
done

echo ""
echo "🚀 Starting Express + Vite on port 5000..."
echo ""

# Start the main Node.js server (includes Vite in middleware mode)
npm run dev
