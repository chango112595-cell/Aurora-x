#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="$(command -v python3 || command -v python || echo python3)"
case "$1" in
  start) $PY "$ROOT/aurora_os.py" start ;;
  stop) pkill -f aurora_os.py || echo "no process found";;
  status) ps aux | grep -E 'aurora_os.py|orchestrator' | grep -v grep ;;
  logs) tail -n 400 "$ROOT/aurora_logs/orchestrator.log";;
  *) echo "usage: $0 {start|stop|status|logs}"; exit 1 ;;
esac
