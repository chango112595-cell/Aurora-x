#!/bin/bash
# Independent AI Systems Manager
# Manages Aurora and Chango as separate, independent systems

echo "🤖 Independent AI Systems Manager"
echo "=================================="
echo ""

# System paths
AURORA_ROOT="/workspaces/Aurora-x"
CHANGO_ROOT="/workspaces/Aurora-x/systems/chango"

# Port assignments (no conflicts)
AURORA_PORTS="5000,5001,5002"  # Aurora: Core, Bridge, Self-Learn
CHANGO_PORTS="6000,6001,6002"  # Chango: Main, Voice, API

show_status() {
    echo "📊 SYSTEM STATUS:"
    echo "=================="
    
    echo "🌟 AURORA STATUS:"
    for port in 5000 5001 5002; do
        if lsof -i :$port >/dev/null 2>&1; then
            echo "   ✅ Port $port: ACTIVE"
        else
            echo "   ❌ Port $port: INACTIVE"
        fi
    done
    
    echo ""
    echo "🎯 CHANGO STATUS:"
    for port in 6000 6001 6002; do
        if lsof -i :$port >/dev/null 2>&1; then
            echo "   ✅ Port $port: ACTIVE"
        else
            echo "   ❌ Port $port: INACTIVE"
        fi
    done
    echo ""
}

start_aurora() {
    echo "🌟 Starting Aurora (Independent System)..."
    cd $AURORA_ROOT
    
    # Start Aurora services on her own ports
    echo "   Starting Aurora Enhanced Core..."
    nohup python3 tools/aurora_enhanced_core.py > logs/aurora_core.log 2>&1 &
    
    echo "   Starting Luminar Nexus..."
    nohup python3 tools/luminar_nexus.py > logs/luminar.log 2>&1 &
    
    echo "   Starting Aurora Frontend..."
    cd client
    nohup npm run dev > ../logs/aurora_frontend.log 2>&1 &
    cd ..
    
    sleep 3
    echo "   ✅ Aurora systems started independently"
}

start_chango() {
    echo "🎯 Starting Chango (Independent System)..."
    cd $CHANGO_ROOT
    
    # Check if dependencies are installed
    if [ ! -d "node_modules" ]; then
        echo "   Installing Chango dependencies..."
        npm install
    fi
    
    echo "   Starting Chango on port 6000..."
    # Modify Chango to use port 6000 to avoid Aurora conflicts
    sed -i 's/PORT=5000/PORT=6000/g' .env 2>/dev/null || echo "PORT=6000" > .env
    
    nohup npm run dev > ../logs/chango.log 2>&1 &
    
    sleep 3
    echo "   ✅ Chango system started independently"
}

stop_aurora() {
    echo "🛑 Stopping Aurora..."
    pkill -f "aurora_enhanced_core\|luminar_nexus\|npm.*dev.*client" 2>/dev/null
    echo "   ✅ Aurora stopped"
}

stop_chango() {
    echo "🛑 Stopping Chango..." 
    pkill -f "tsx.*server/index\|npm.*dev.*chango" 2>/dev/null
    echo "   ✅ Chango stopped"
}

case "$1" in
    "aurora")
        stop_aurora
        start_aurora
        ;;
    "chango") 
        stop_chango
        start_chango
        ;;
    "both")
        echo "🚀 Starting both systems independently..."
        stop_aurora
        stop_chango
        sleep 2
        start_aurora
        sleep 3
        start_chango
        ;;
    "stop")
        stop_aurora
        stop_chango
        ;;
    "status")
        show_status
        ;;
    *)
        echo "Usage: $0 {aurora|chango|both|stop|status}"
        echo ""
        echo "Commands:"
        echo "  aurora  - Start only Aurora system"
        echo "  chango  - Start only Chango system"  
        echo "  both    - Start both systems independently"
        echo "  stop    - Stop both systems"
        echo "  status  - Show system status"
        echo ""
        echo "🤖 Independent AI Architecture:"
        echo "   Aurora: Offline AI Doctor (ports 5000-5002)"
        echo "   Chango: Omnipresent JARVIS (ports 6000-6002)"
        echo "   Both systems operate independently!"
        ;;
esac