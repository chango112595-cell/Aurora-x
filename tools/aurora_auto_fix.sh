#!/bin/bash
#
# Aurora's Auto-Fix Script
# She knows what's wrong and will fix it herself!
#

echo "🌟 Aurora: I found the issues! Let me fix them..."
echo "======================================================================"
echo ""

# Step 1: Install client dependencies
echo "📦 Aurora: Installing client dependencies..."
cd /workspaces/Aurora-x/client
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "======================================================================"
echo "🚀 Aurora: Now attempting to start servers..."
echo "======================================================================"
echo ""

# Step 2: Start servers with Luminar Nexus
python3 /workspaces/Aurora-x/tools/luminar_nexus.py start-all

echo ""
echo "======================================================================"
echo "📊 Aurora: Checking server status..."
echo "======================================================================"
echo ""

sleep 3

# Step 3: Check status
python3 /workspaces/Aurora-x/tools/luminar_nexus.py status

echo ""
echo "✨ Aurora: All done! Check the PORTS tab in VS Code!"
echo "   Port 5173 should be forwarded for Vite"
echo ""
