#!/bin/bash
# Aurora-X Development Server Manager
# Manages backend (port 5000) and frontend Vite (port 5001)

set -e

PROJECT_ROOT="/workspaces/Aurora-x"
BACKEND_LOG="/tmp/backend.log"
VITE_LOG="/tmp/vite.log"
BACKEND_PID="/tmp/backend.pid"
VITE_PID="/tmp/vite.pid"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
  echo -e "${RED}[✗]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[!]${NC} $1"
}

# Check if process is running
is_running() {
  local pid=$1
  if [ -z "$pid" ]; then
    return 1
  fi
  kill -0 "$pid" 2>/dev/null && return 0 || return 1
}

# Get running port for a process
get_port_status() {
  local port=$1
  if ss -ltnp 2>/dev/null | grep -q ":$port "; then
    echo "listening"
  else
    echo "not-listening"
  fi
}

# Start backend
start_backend() {
  log_info "Starting backend (Express + TypeScript)..."
  
  if [ -f "$BACKEND_PID" ]; then
    local old_pid=$(cat "$BACKEND_PID" 2>/dev/null)
    if is_running "$old_pid" 2>/dev/null; then
      log_warn "Backend already running (PID: $old_pid)"
      return 0
    fi
  fi
  
  cd "$PROJECT_ROOT"
  nohup npm run dev > "$BACKEND_LOG" 2>&1 &
  local new_pid=$!
  echo "$new_pid" > "$BACKEND_PID"
  
  # Wait for startup
  sleep 2
  
  if is_running "$new_pid"; then
    log_success "Backend started (PID: $new_pid, port 5000)"
    return 0
  else
    log_error "Backend failed to start. Check logs: tail -f $BACKEND_LOG"
    return 1
  fi
}

# Start Vite frontend
start_vite() {
  log_info "Starting Vite frontend (React + TypeScript)..."
  
  if [ -f "$VITE_PID" ]; then
    local old_pid=$(cat "$VITE_PID" 2>/dev/null)
    if is_running "$old_pid" 2>/dev/null; then
      log_warn "Vite already running (PID: $old_pid)"
      return 0
    fi
  fi
  
  cd "$PROJECT_ROOT"
  nohup npx vite --host 0.0.0.0 --port 5001 > "$VITE_LOG" 2>&1 &
  local new_pid=$!
  echo "$new_pid" > "$VITE_PID"
  
  # Wait for startup
  sleep 2
  
  if is_running "$new_pid"; then
    log_success "Vite started (PID: $new_pid, port 5001)"
    return 0
  else
    log_error "Vite failed to start. Check logs: tail -f $VITE_LOG"
    return 1
  fi
}

# Stop backend
stop_backend() {
  log_info "Stopping backend..."
  
  if [ -f "$BACKEND_PID" ]; then
    local pid=$(cat "$BACKEND_PID")
    if is_running "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      sleep 1
      if ! is_running "$pid" 2>/dev/null; then
        log_success "Backend stopped (was PID: $pid)"
        rm -f "$BACKEND_PID"
        return 0
      else
        kill -9 "$pid" 2>/dev/null || true
        log_success "Backend force-stopped (was PID: $pid)"
        rm -f "$BACKEND_PID"
        return 0
      fi
    else
      log_warn "Backend not running"
      rm -f "$BACKEND_PID"
      return 0
    fi
  else
    log_warn "No backend PID file found"
    return 0
  fi
}

# Stop Vite
stop_vite() {
  log_info "Stopping Vite..."
  
  if [ -f "$VITE_PID" ]; then
    local pid=$(cat "$VITE_PID")
    if is_running "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      sleep 1
      if ! is_running "$pid" 2>/dev/null; then
        log_success "Vite stopped (was PID: $pid)"
        rm -f "$VITE_PID"
        return 0
      else
        kill -9 "$pid" 2>/dev/null || true
        log_success "Vite force-stopped (was PID: $pid)"
        rm -f "$VITE_PID"
        return 0
      fi
    else
      log_warn "Vite not running"
      rm -f "$VITE_PID"
      return 0
    fi
  else
    log_warn "No Vite PID file found"
    return 0
  fi
}

# Status check
status() {
  echo ""
  log_info "Development Server Status"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # Backend status
  if [ -f "$BACKEND_PID" ]; then
    local backend_pid=$(cat "$BACKEND_PID")
    if is_running "$backend_pid" 2>/dev/null; then
      local port_status=$(get_port_status 5000)
      if [ "$port_status" = "listening" ]; then
        log_success "Backend: RUNNING (PID: $backend_pid, port 5000)"
      else
        log_warn "Backend: RUNNING BUT NOT LISTENING (PID: $backend_pid, port 5000)"
      fi
    else
      log_error "Backend: STOPPED (stale PID: $backend_pid)"
    fi
  else
    log_error "Backend: NOT RUNNING"
  fi
  
  # Vite status
  if [ -f "$VITE_PID" ]; then
    local vite_pid=$(cat "$VITE_PID")
    if is_running "$vite_pid" 2>/dev/null; then
      local port_status=$(get_port_status 5001)
      if [ "$port_status" = "listening" ]; then
        log_success "Vite:    RUNNING (PID: $vite_pid, port 5001)"
      else
        log_warn "Vite: RUNNING BUT NOT LISTENING (PID: $vite_pid, port 5001)"
      fi
    else
      log_error "Vite:    STOPPED (stale PID: $vite_pid)"
    fi
  else
    log_error "Vite:    NOT RUNNING"
  fi
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "Access URLs:"
  echo "  Frontend: http://localhost:5001"
  echo "  Backend:  http://localhost:5000"
  echo ""
}

# Tail logs
tail_logs() {
  log_info "Tailing logs (Ctrl+C to stop)..."
  echo ""
  
  # Create named pipes for simultaneous tail
  mkfifo /tmp/backend_tail /tmp/vite_tail 2>/dev/null || true
  
  # Start tails in background
  tail -f "$BACKEND_LOG" > /tmp/backend_tail &
  local backend_tail_pid=$!
  
  tail -f "$VITE_LOG" > /tmp/vite_tail &
  local vite_tail_pid=$!
  
  # Interleave the tails
  (
    while true; do
      if read -t 0.1 line < /tmp/backend_tail; then
        echo -e "${BLUE}[BACKEND]${NC} $line"
      fi
      if read -t 0.1 line < /tmp/vite_tail; then
        echo -e "${YELLOW}[VITE]${NC} $line"
      fi
    done
  ) &
  
  local main_pid=$!
  trap "kill $backend_tail_pid $vite_tail_pid $main_pid 2>/dev/null; rm -f /tmp/backend_tail /tmp/vite_tail" EXIT
  wait $main_pid 2>/dev/null || true
}

# Main command handler
case "${1:-start}" in
  start)
    log_info "Starting Aurora-X development servers..."
    start_backend
    start_vite
    status
    log_success "All servers started! 🚀"
    echo ""
    echo "Next steps:"
    echo "  • Open http://localhost:5001 in your browser"
    echo "  • View logs: $0 logs"
    echo "  • Check status: $0 status"
    echo "  • Stop servers: $0 stop"
    ;;
    
  stop)
    log_info "Stopping Aurora-X development servers..."
    stop_vite
    stop_backend
    log_success "All servers stopped ✓"
    ;;
    
  restart)
    log_info "Restarting Aurora-X development servers..."
    stop_vite
    stop_backend
    sleep 1
    start_backend
    start_vite
    status
    log_success "All servers restarted! 🚀"
    ;;
    
  status)
    status
    ;;
    
  logs)
    tail_logs
    ;;
    
  backend-logs)
    log_info "Tailing backend logs (Ctrl+C to stop)..."
    tail -f "$BACKEND_LOG"
    ;;
    
  vite-logs)
    log_info "Tailing Vite logs (Ctrl+C to stop)..."
    tail -f "$VITE_LOG"
    ;;
    
  kill)
    log_warn "Force-killing all processes..."
    pkill -f "npm run dev" || true
    pkill -f "vite" || true
    rm -f "$BACKEND_PID" "$VITE_PID"
    sleep 1
    status
    ;;
    
  *)
    echo "Aurora-X Development Server Manager"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start         Start both backend and frontend servers (default)"
    echo "  stop          Stop both servers gracefully"
    echo "  restart       Restart both servers"
    echo "  status        Show server status and listening ports"
    echo "  logs          Tail both logs simultaneously (interleaved)"
    echo "  backend-logs  Tail backend logs only"
    echo "  vite-logs     Tail Vite logs only"
    echo "  kill          Force-kill all processes (emergency)"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start servers"
    echo "  $0 status         # Check what's running"
    echo "  $0 logs           # Watch logs in real-time"
    echo "  $0 restart        # Restart both servers"
    echo ""
    exit 1
    ;;
esac
