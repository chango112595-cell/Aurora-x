#!/bin/bash
#
# Aurora Complete Server Startup & Monitor Script
# Ensures everything works and keeps running!
#

echo "════════════════════════════════════════════════════════════════════"
echo "🌟 AURORA COMPLETE SERVER STARTUP"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Start all servers with enhanced Luminar Nexus
python3 /workspaces/Aurora-x/tools/luminar_nexus.py start-all

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "🎉 SERVERS STARTED!"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Current Status:"
python3 /workspaces/Aurora-x/tools/luminar_nexus.py status

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "💡 USEFUL COMMANDS:"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "  📋 View Vite logs:     python3 tools/luminar_nexus.py logs vite"
echo "  📋 View Backend logs:  python3 tools/luminar_nexus.py logs backend"
echo "  📊 Check status:       python3 tools/luminar_nexus.py status"
echo "  🔄 Restart Vite:       python3 tools/luminar_nexus.py restart vite"
echo "  🩺 Auto-heal mode:     python3 tools/luminar_nexus.py monitor"
echo "  🛑 Stop all:           python3 tools/luminar_nexus.py stop-all"
echo ""
echo "  🌐 Open Vite in browser: http://localhost:5173"
echo "  🔌 Check PORTS tab in VS Code to access forwarded ports"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""
