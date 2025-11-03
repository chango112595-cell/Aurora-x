#!/bin/bash
# 🚀 Aurora ONE-COMMAND Startup Script
# Single command to start everything and open the control center

set -e

echo "🌌 Aurora Starting..."
echo "================================"

cd /workspaces/Aurora-x

# Start Aurora using unified command manager
python3 aurora_unified_cmd.py start

# Give services a moment to start
sleep 3

echo ""
echo "================================"
echo "✅ Aurora is ready!"
echo ""
echo "🎮 Control Center: http://localhost:5000/control"
echo "📊 Dashboard:      http://localhost:5000/"
echo "💬 Chat:           http://localhost:5000/chat"
echo "🔧 Bridge API:     http://localhost:5001/docs"
echo ""
echo "All commands can now be run from the Control Center buttons!"
echo "================================"
