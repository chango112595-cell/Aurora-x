#!/bin/bash
# Aurora-X Ultra v3 - One-tap commands

SPEC3="${1:-specs/check_palindrome.md}"
DISCORD="tools/discord_cli.py"

case "${2:-spec3-all}" in
  serve-v3)
    echo "🚀 Starting FastAPI server on port ${AURORA_PORT:-5001}..."
    uvicorn aurora_x.serve:app --host 0.0.0.0 --port ${AURORA_PORT:-5001}
    ;;
    
  open-dashboard)
    PORT=${AURORA_PORT:-5001}
    HOST="${REPL_SLUG:+${REPL_SLUG}.${REPL_OWNER}.repl.co}"
    if [ -n "$HOST" ]; then
      URL="https://$HOST/dashboard/spec_runs"
    else
      URL="http://localhost:$PORT/dashboard/spec_runs"
    fi
    echo "🌌 Dashboard → $URL"
    URL=$URL python -c "import webbrowser,os; webbrowser.open(os.environ.get('URL',''))" 2>/dev/null || true
    ;;
    
  open-report)
    latest=$(ls -dt runs/run-* 2>/dev/null | head -1)
    if [ -z "$latest" ]; then 
      echo "No runs found"
      exit 1
    fi
    echo "📖 Opening report: $latest/report.html"
    python -c "import webbrowser,os; webbrowser.open('file://' + os.path.abspath('$latest/report.html'))" 2>/dev/null || true
    ;;
    
  orchestrator)
    echo "🌌 Starting Aurora-X T07 Orchestrator..."
    echo "📝 Environment config:"
    echo "  AURORA_ORCH_INTERVAL=${AURORA_ORCH_INTERVAL:-300} seconds"
    echo "  AURORA_GIT_AUTO=${AURORA_GIT_AUTO:-0}"
    echo "  AURORA_GIT_BRANCH=${AURORA_GIT_BRANCH:-main}"
    echo "  AURORA_GIT_URL=${AURORA_GIT_URL:-Not set}"
    python aurora_x/orchestrator.py
    ;;
    
  orchestrate-bg)
    nohup python aurora_x/orchestrator.py >/tmp/aurora_orch.log 2>&1 &
    echo "🚀 Daemon started (PID: $!)"
    echo "📝 Logs: /tmp/aurora_orch.log"
    echo "📊 To monitor: tail -f /tmp/aurora_orch.log"
    echo "⚠️  To stop: pkill -f 'python aurora_x/orchestrator.py'"
    ;;
    
  orch-test)
    echo "🧪 Testing orchestrator (5 second interval, no git)..."
    AURORA_ORCH_INTERVAL=5 AURORA_GIT_AUTO=0 timeout 15 python aurora_x/orchestrator.py || true
    echo "✅ Orchestrator test completed"
    ;;
    
  orch-status)
    echo "🔍 Orchestrator environment status:"
    echo "  Poll interval: ${AURORA_ORCH_INTERVAL:-300} seconds"
    echo "  Git auto-commit: ${AURORA_GIT_AUTO:-0}"
    echo "  Git branch: ${AURORA_GIT_BRANCH:-main}"
    echo "  Git URL: ${AURORA_GIT_URL:-Not configured}"
    echo ""
    echo "📊 Specs being monitored:"
    ls -la specs/*.md 2>/dev/null | awk '{print "  - " $9}' || echo "  No specs found"
    echo ""
    echo "📝 Recent runs:"
    tail -3 runs/spec_runs.jsonl 2>/dev/null | while read line; do
      echo "  $(echo $line | python -c "import sys,json; d=json.loads(sys.stdin.read()); print(f'{d[\"timestamp\"]}: {d[\"spec\"]} - {d[\"status\"]}')" 2>/dev/null || echo $line)"
    done || echo "  No recent runs"
    ;;
    
  spec3)
    echo "🔧 v3 compile: $SPEC3"
    python tools/spec_compile_v3.py "$SPEC3" || {
      [ -f "$DISCORD" ] && python "$DISCORD" error "❌ v3 compile failed: $SPEC3"
      exit 1
    }
    ;;
    
  spec3-test)
    latest=$(ls -dt runs/run-* 2>/dev/null | head -1)
    if [ -z "$latest" ]; then 
      echo "No runs found"
      exit 1
    fi
    python -m unittest discover -s "$latest/tests" -t "$latest" || {
      [ -f "$DISCORD" ] && python "$DISCORD" error "❌ v3 tests failed for $(basename $latest)"
      exit 1
    }
    ;;
    
  spec3-all)
    echo "🔧 v3 compile: $SPEC3"
    python tools/spec_compile_v3.py "$SPEC3" || {
      [ -f "$DISCORD" ] && python "$DISCORD" error "❌ v3 compile failed: $SPEC3"
      exit 1
    }
    
    latest=$(ls -dt runs/run-* 2>/dev/null | head -1)
    if [ -z "$latest" ]; then 
      echo "No runs found"
      exit 1
    fi
    
    echo "🧪 Testing $latest..."
    python -m unittest discover -s "$latest/tests" -t "$latest" || {
      [ -f "$DISCORD" ] && python "$DISCORD" error "❌ v3 tests failed for $(basename $latest)"
      exit 1
    }
    
    echo "📊 Report: $latest/report.html   |   Dashboard: /dashboard/spec_runs"
    [ -f "$DISCORD" ] && python "$DISCORD" success "✅ v3 spec passed: $SPEC3 — $(basename $latest)"
    ;;
    
  say)
    WHAT="${SPEC3:-reverse a string}"
    echo "🗣  NL → Spec → Code: $WHAT"
    python -m aurora_x.main --nl "$WHAT"
    ;;
    
  *)
    echo "Usage: ./make_v3.sh [spec.md] [command]"
    echo "Commands:"
    echo "  serve-v3        - Start FastAPI server"
    echo "  open-dashboard  - Open dashboard URL in browser"
    echo "  open-report     - Open latest run's HTML report"
    echo "  spec3           - Compile v3 spec"
    echo "  spec3-test      - Test latest run"
    echo "  spec3-all       - Compile, test, and notify (default)"
    echo ""
    echo "Orchestrator commands:"
    echo "  orchestrator    - Start continuous spec monitoring daemon"
    echo "  orchestrate-bg  - Start daemon in background"
    echo "  orch-test       - Test orchestrator (15 sec quick test)"
    echo "  orch-status     - Show orchestrator environment status"
    echo ""
    echo "T08 Natural Language:"
    echo "  say             - Convert English to spec and code"
    echo ""
    echo "Examples:"
    echo "  ./make_v3.sh specs/check_palindrome.md spec3-all"
    echo "  ./make_v3.sh 'reverse a string' say"
    echo "  ./make_v3.sh - orchestrator"
    echo "  AURORA_GIT_AUTO=1 ./make_v3.sh - orchestrator"
    ;;
esac