#!/bin/bash
# Aurora-X Ultra v3 - One-tap commands

SPEC3="${1:-specs/check_palindrome.md}"
DISCORD="tools/discord_cli.py"

case "${2:-spec3-all}" in
  serve-v3)
    echo "🚀 Starting FastAPI server..."
    uvicorn aurora_x.serve:app --host 0.0.0.0 --port ${PORT:-5000}
    ;;
    
  open-dashboard)
    PORT=${PORT:-5000}
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
    echo "Examples:"
    echo "  ./make_v3.sh specs/check_palindrome.md spec3-all"
    echo "  ./make_v3.sh specs/fibonacci_sequence.md spec3"
    echo "  ./make_v3.sh - serve-v3"
    echo "  ./make_v3.sh - open-dashboard"
    echo "  ./make_v3.sh - open-report"
    ;;
esac