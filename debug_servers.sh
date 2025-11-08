#!/bin/bash
#
# Intensive Server Debugging Script
# Find out exactly why servers won't stay alive
#

echo "🔍 INTENSIVE SERVER DEBUGGING"
echo "========================================================================"
echo ""

echo "Step 1: Check if dependencies are installed"
echo "----------------------------------------"
if [ -d "/workspaces/Aurora-x/client/node_modules" ]; then
    echo "✅ client/node_modules exists"
else
    echo "❌ client/node_modules MISSING - Installing now..."
    cd /workspaces/Aurora-x/client && npm install
fi

echo ""
echo "Step 2: Test if npm run dev command works AT ALL"
echo "----------------------------------------"
cd /workspaces/Aurora-x/client
timeout 5 npm run dev > /tmp/vite_test.log 2>&1 &
NPM_PID=$!
sleep 3

if ps -p $NPM_PID > /dev/null; then
    echo "✅ npm run dev is RUNNING (PID: $NPM_PID)"
    kill $NPM_PID 2>/dev/null
    echo "📋 First few lines of output:"
    head -20 /tmp/vite_test.log
else
    echo "❌ npm run dev DIED immediately"
    echo "📋 Full error output:"
    cat /tmp/vite_test.log
fi

echo ""
echo "Step 3: Check if tmux can actually run the command"
echo "----------------------------------------"
tmux kill-session -t test-vite 2>/dev/null
tmux new-session -d -s test-vite "cd /workspaces/Aurora-x/client && npm run dev"

sleep 3

if tmux has-session -t test-vite 2>/dev/null; then
    echo "✅ tmux session 'test-vite' is ALIVE"
    echo "📋 Capturing tmux output:"
    tmux capture-pane -pt test-vite -S -20
    
    echo ""
    echo "🌐 Checking if port 5173 is listening:"
    netstat -tuln | grep 5173 || echo "❌ Port 5173 NOT listening"
    
else
    echo "❌ tmux session DIED"
fi

echo ""
echo "Step 4: Check what's actually running"
echo "----------------------------------------"
echo "Process list:"
ps aux | grep -E "(npm|vite|node)" | grep -v grep

echo ""
echo "Listening ports:"
netstat -tuln | grep -E "(5173|5001)"

echo ""
echo "Step 5: Try DIRECT node command (bypass npm)"
echo "----------------------------------------"
cd /workspaces/Aurora-x/client
if [ -f "node_modules/.bin/vite" ]; then
    echo "Testing direct vite command..."
    timeout 5 node_modules/.bin/vite > /tmp/direct_vite.log 2>&1 &
    VITE_PID=$!
    sleep 3
    
    if ps -p $VITE_PID > /dev/null; then
        echo "✅ Direct vite command WORKS (PID: $VITE_PID)"
        kill $VITE_PID 2>/dev/null
        head -20 /tmp/direct_vite.log
    else
        echo "❌ Direct vite command also failed"
        cat /tmp/direct_vite.log
    fi
else
    echo "❌ vite binary not found in node_modules"
fi

echo ""
echo "========================================================================"
echo "🔍 DIAGNOSIS COMPLETE"
echo "========================================================================"
echo ""
echo "📊 Summary:"
echo "  - Check if npm install completed successfully above"
echo "  - Check if tmux session stayed alive"
echo "  - Check if port 5173 is listening"
echo "  - Review error messages in logs above"
echo ""
echo "💡 To view live tmux session: tmux attach -t test-vite"
echo "   (Press Ctrl+B then D to detach)"
echo ""
