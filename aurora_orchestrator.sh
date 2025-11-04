#!/bin/bash
#
# Aurora Orchestrator - Single command to manage all services
# Built by Aurora - Because manual ops are for humans, not experts
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/workspaces/Aurora-x"
VENV_PATH="$PROJECT_ROOT/.venv"
SUPERVISOR_SCRIPT="$PROJECT_ROOT/tools/aurora_supervisor.py"
CONFIG_FILE="$PROJECT_ROOT/aurora_supervisor_config.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║                                                       ║"
    echo "║          🌟 AURORA SERVICE ORCHESTRATOR 🌟          ║"
    echo "║                                                       ║"
    echo "║         Self-Healing · Auto-Restart · Expert         ║"
    echo "║                                                       ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

function activate_venv() {
    if [ -d "$VENV_PATH" ]; then
        source "$VENV_PATH/bin/activate"
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    else
        echo -e "${YELLOW}⚠️  No virtual environment found at $VENV_PATH${NC}"
    fi
}

function check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Python3 found${NC}"
    
    # Check Node/npm
    if ! command -v npm &> /dev/null; then
        echo -e "${YELLOW}⚠️  npm not found (Aurora UI won't start)${NC}"
    else
        echo -e "${GREEN}✅ npm found${NC}"
    fi
    
    # Check supervisor script
    if [ ! -f "$SUPERVISOR_SCRIPT" ]; then
        echo -e "${RED}❌ Supervisor script not found at $SUPERVISOR_SCRIPT${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Supervisor script found${NC}"
    
    # Check dependencies
    activate_venv
    python3 -c "import psutil, requests" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Installing required Python packages...${NC}"
        pip install -q psutil requests
    fi
    echo -e "${GREEN}✅ Python dependencies satisfied${NC}"
}

function start_all() {
    print_banner
    check_prerequisites
    
    echo -e "${BLUE}🚀 Starting all Aurora services...${NC}"
    echo ""
    
    cd "$PROJECT_ROOT"
    activate_venv
    
    # Start supervisor in background
    nohup python3 "$SUPERVISOR_SCRIPT" start > /tmp/aurora_orchestrator.log 2>&1 &
    SUPERVISOR_PID=$!
    
    echo -e "${GREEN}✅ Supervisor started (PID: $SUPERVISOR_PID)${NC}"
    echo -e "${BLUE}📊 Waiting for services to come online...${NC}"
    
    sleep 5
    
    # Show status
    status
}

function stop_all() {
    echo -e "${BLUE}🛑 Stopping all Aurora services...${NC}"
    
    cd "$PROJECT_ROOT"
    activate_venv
    
    python3 "$SUPERVISOR_SCRIPT" stop
    
    # Also kill any stray processes
    pkill -f "aurora_supervisor.py" || true
    pkill -f "npm run dev" || true
    pkill -f "uvicorn aurora_x.serve" || true
    pkill -f "aurora_x.self_learn_server" || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
}

function restart_all() {
    echo -e "${BLUE}🔄 Restarting all Aurora services...${NC}"
    stop_all
    sleep 3
    start_all
}

function status() {
    cd "$PROJECT_ROOT"
    activate_venv
    
    echo -e "${BLUE}📊 Service Status:${NC}"
    echo ""
    
    python3 "$SUPERVISOR_SCRIPT" status | python3 -m json.tool
    
    echo ""
    echo -e "${BLUE}🔌 Port Status:${NC}"
    lsof -i -P -n | grep -E "5000|5001|5002|8080" | head -10 || echo "No services listening"
}

function quick_check() {
    echo -e "${BLUE}⚡ Quick Health Check:${NC}"
    
    ports=(5000 5001 5002 8080)
    names=("Aurora UI" "Backend API" "Self-Learning" "File Server")
    
    for i in "${!ports[@]}"; do
        port="${ports[$i]}"
        name="${names[$i]}"
        
        if lsof -i ":$port" -t > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name (port $port)${NC}"
        else
            echo -e "${RED}❌ $name (port $port)${NC}"
        fi
    done
}

function tail_logs() {
    echo -e "${BLUE}📜 Tailing logs (Ctrl+C to stop):${NC}"
    echo ""
    
    tail -f /tmp/aurora_supervisor.log /tmp/aurora_orchestrator.log /tmp/aurora_uvicorn_5001.log /tmp/aurora_self_learn.log 2>/dev/null
}

function health_dashboard() {
    echo -e "${BLUE}🌐 Opening health dashboard...${NC}"
    
    cd "$PROJECT_ROOT"
    activate_venv
    
    if [ -f "$PROJECT_ROOT/tools/aurora_health_dashboard.py" ]; then
        python3 "$PROJECT_ROOT/tools/aurora_health_dashboard.py" &
        echo -e "${GREEN}✅ Dashboard running at http://localhost:9090${NC}"
    else
        echo -e "${YELLOW}⚠️  Health dashboard not yet implemented${NC}"
    fi
}

function show_help() {
    print_banner
    echo "Usage: ./aurora_orchestrator.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services with supervisor"
    echo "  stop        Stop all services gracefully"
    echo "  restart     Restart all services"
    echo "  status      Show detailed service status"
    echo "  check       Quick port health check"
    echo "  logs        Tail all service logs"
    echo "  dashboard   Open health monitoring dashboard"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./aurora_orchestrator.sh start"
    echo "  ./aurora_orchestrator.sh status"
    echo "  ./aurora_orchestrator.sh check"
}

# Main command router
case "${1:-help}" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        status
        ;;
    check)
        quick_check
        ;;
    logs)
        tail_logs
        ;;
    dashboard)
        health_dashboard
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
