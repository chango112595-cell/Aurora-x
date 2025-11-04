#!/bin/bash
# Luminar Nexus Auto-Keeper
# Ensures Luminar stays running and servers persist
# Runs as background daemon with auto-restart

set -e

PROJECT_ROOT="/workspaces/Aurora-x"
LUMINAR_SCRIPT="$PROJECT_ROOT/tools/luminar_nexus.py"
KEEPER_PID_FILE="/tmp/luminar_keeper.pid"
KEEPER_LOG="/tmp/luminar_keeper.log"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
  echo -e "${BLUE}[KEEPER]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$KEEPER_LOG"
}

log_success() {
  echo -e "${GREEN}[✓]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$KEEPER_LOG"
}

log_error() {
  echo -e "${RED}[✗]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$KEEPER_LOG"
}

log_warn() {
  echo -e "${YELLOW}[!]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$KEEPER_LOG"
}

# Check if Luminar servers are healthy
check_luminar_health() {
  # Check backend
  if ! curl -s -I http://localhost:5000 > /dev/null 2>&1; then
    return 1
  fi
  
  # Check frontend
  if ! curl -s -I http://localhost:5001 > /dev/null 2>&1; then
    return 1
  fi
  
  return 0
}

# Ensure tmux is installed
ensure_tmux() {
  if ! command -v tmux &> /dev/null; then
    log_warn "tmux not found, installing..."
    sudo apt-get update >/dev/null 2>&1 || true
    sudo apt-get install -y tmux >/dev/null 2>&1 || true
  fi
}

# Start Luminar servers via tmux
start_luminar_servers() {
  log_info "Starting Luminar servers..."
  
  cd "$PROJECT_ROOT"
  python3 "$LUMINAR_SCRIPT" start-all >> "$KEEPER_LOG" 2>&1
  
  if [ $? -eq 0 ]; then
    log_success "Luminar servers started successfully"
    return 0
  else
    log_error "Failed to start Luminar servers"
    return 1
  fi
}

# Main keeper loop
keeper_loop() {
  log_info "🌟 Luminar Keeper started (PID: $$)"
  log_info "Watching Aurora servers every 30 seconds..."
  
  local restart_count=0
  
  while true; do
    if check_luminar_health; then
      # Servers healthy
      if [ $restart_count -gt 0 ]; then
        log_success "Servers recovered! Health checks passing."
        restart_count=0
      fi
    else
      # Servers unhealthy
      restart_count=$((restart_count + 1))
      log_warn "Health check FAILED (attempt #$restart_count). Restarting servers..."
      
      # Try to restart
      start_luminar_servers
      sleep 5  # Give servers time to start
      
      if ! check_luminar_health; then
        log_error "Restart failed! Servers still not responding."
      else
        log_success "Restart successful!"
        restart_count=0
      fi
    fi
    
    # Sleep and check again
    sleep 30
  done
}

# Start keeper in background
start_keeper() {
  ensure_tmux
  
  # Check if keeper already running
  if [ -f "$KEEPER_PID_FILE" ]; then
    local old_pid=$(cat "$KEEPER_PID_FILE")
    if ps -p "$old_pid" > /dev/null 2>&1; then
      log_warn "Luminar Keeper already running (PID: $old_pid)"
      return 0
    fi
  fi
  
  # Start servers immediately
  start_luminar_servers
  sleep 3
  
  # Start keeper in background
  nohup bash -c "
    cd '$PROJECT_ROOT'
    keeper_loop
  " > "$KEEPER_LOG" 2>&1 &
  
  local keeper_pid=$!
  echo "$keeper_pid" > "$KEEPER_PID_FILE"
  
  log_success "Luminar Keeper started (PID: $keeper_pid)"
  log_info "Logs: tail -f $KEEPER_LOG"
  log_info "Status: $0 status"
}

# Stop keeper
stop_keeper() {
  if [ -f "$KEEPER_PID_FILE" ]; then
    local keeper_pid=$(cat "$KEEPER_PID_FILE")
    if ps -p "$keeper_pid" > /dev/null 2>&1; then
      log_info "Stopping Luminar Keeper (PID: $keeper_pid)..."
      kill "$keeper_pid" 2>/dev/null || true
      
      # Also stop Luminar servers
      log_info "Stopping Luminar servers..."
      cd "$PROJECT_ROOT"
      python3 "$LUMINAR_SCRIPT" stop-all >> "$KEEPER_LOG" 2>&1 || true
      
      rm -f "$KEEPER_PID_FILE"
      log_success "Luminar Keeper stopped"
      return 0
    fi
  fi
  
  log_warn "Luminar Keeper not running"
  return 0
}

# Show status
show_status() {
  echo ""
  log_info "Luminar Keeper Status"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # Keeper status
  if [ -f "$KEEPER_PID_FILE" ]; then
    local keeper_pid=$(cat "$KEEPER_PID_FILE")
    if ps -p "$keeper_pid" > /dev/null 2>&1; then
      log_success "Keeper: RUNNING (PID: $keeper_pid)"
    else
      log_error "Keeper: STOPPED (stale PID: $keeper_pid)"
    fi
  else
    log_error "Keeper: NOT RUNNING"
  fi
  
  # Luminar servers status
  echo ""
  cd "$PROJECT_ROOT"
  python3 "$LUMINAR_SCRIPT" status 2>&1 | tail -n 20
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
}

# Show logs
show_logs() {
  log_info "Tailing Luminar Keeper logs (Ctrl+C to stop)..."
  tail -f "$KEEPER_LOG"
}

# Main command handler
case "${1:-start}" in
  start)
    start_keeper
    show_status
    ;;
    
  stop)
    stop_keeper
    ;;
    
  restart)
    stop_keeper
    sleep 2
    start_keeper
    show_status
    ;;
    
  status)
    show_status
    ;;
    
  logs)
    show_logs
    ;;
    
  *)
    echo "Luminar Nexus Auto-Keeper"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start      Start Luminar Keeper (watches and restarts servers) - DEFAULT"
    echo "  stop       Stop Luminar Keeper and servers"
    echo "  restart    Restart Luminar Keeper"
    echo "  status     Show Keeper and server status"
    echo "  logs       Tail Keeper logs in real-time"
    echo ""
    echo "Examples:"
    echo "  $0 start       # Start Keeper (servers auto-managed)"
    echo "  $0 status      # Check health of all servers"
    echo "  $0 logs        # Watch Keeper activity"
    echo ""
    exit 1
    ;;
esac
