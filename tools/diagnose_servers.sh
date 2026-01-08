#!/bin/bash

echo "🔍 AURORA SERVER DIAGNOSTICS"
echo "=============================="
echo ""

echo "1️⃣ Checking if client directory exists..."
if [ -d "/workspaces/Aurora-x/client" ]; then
    echo "   ✅ Client directory exists"
    cd /workspaces/Aurora-x/client

    echo ""
    echo "2️⃣ Checking for package.json..."
    if [ -f "package.json" ]; then
        echo "   ✅ package.json exists"
        echo ""
        echo "3️⃣ Checking scripts in package.json..."
        cat package.json | grep -A 10 "scripts"

        echo ""
        echo "4️⃣ Checking if node_modules exists..."
        if [ -d "node_modules" ]; then
            echo "   ✅ node_modules exists"
        else
            echo "   ❌ node_modules NOT found - need to run npm install"
        fi

        echo ""
        echo "5️⃣ Testing npm run dev command..."
        timeout 5 npm run dev 2>&1 | head -20
    else
        echo "   ❌ package.json NOT found"
    fi
else
    echo "   ❌ Client directory NOT found"
fi

echo ""
echo "6️⃣ Checking tmux sessions..."
tmux ls 2>&1 || echo "   No tmux sessions running"

echo ""
echo "7️⃣ If tmux sessions exist, capturing last output..."
tmux capture-pane -pt aurora-vite -S -20 2>/dev/null || echo "   No aurora-vite session"
