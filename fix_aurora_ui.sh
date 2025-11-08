#!/bin/bash
# Aurora UI Fix - Correct Browser Opening
# Fixes Aurora opening wrong port in browser

echo "🔧 AURORA UI FIX"
echo "==============="
echo ""

# Kill any processes auto-opening wrong ports
pkill -f "chrome.*5003" 2>/dev/null
pkill -f "browser.*5003" 2>/dev/null

echo "✅ Stopped auto-opening incorrect port 5003"

# Configure Aurora to use correct ports
echo "🌟 Aurora Correct Endpoints:"
echo "   Frontend UI: http://localhost:5173"
echo "   Chat API: http://localhost:5003/api/chat" 
echo "   Bridge API: http://localhost:5001/api"
echo "   Backend API: http://localhost:5002/api"
echo ""

# Check if frontend is actually serving the UI
if curl -s localhost:5173 | grep -q "html"; then
    echo "✅ Frontend is serving UI on port 5173"
    echo "🚀 Opening Aurora's correct UI..."
    
    # Open the correct frontend URL
    if command -v code >/dev/null 2>&1; then
        code --open-url http://localhost:5173
    fi
else
    echo "❌ Frontend not properly serving UI"
    echo "🔧 Restarting Aurora frontend..."
    cd /workspaces/Aurora-x
    tmux kill-session -t aurora-vite 2>/dev/null
    cd client
    tmux new-session -d -s aurora-vite "npm run dev"
    sleep 5
    echo "✅ Frontend restarted"
fi

echo ""
echo "🎯 AURORA ACCESS POINTS:"
echo "   Main UI: http://localhost:5173 (Use this one!)"
echo "   Chat API: http://localhost:5003/api/chat"
echo "   Status: http://localhost:5001/status"
echo ""
echo "💡 If Aurora auto-opens browser, use port 5173, NOT 5003!"