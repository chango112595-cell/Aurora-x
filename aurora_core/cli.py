#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "aurora_core"))
from orchestrator import main_loop

def usage():
    print("usage: python -m aurora_core.cli start|stop|status (stop/status are basic)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage(); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "start":
        main_loop()
    elif cmd == "status":
        print("status: processes in .aurora/pids (inspect logs in aurora_logs)")
    elif cmd == "stop":
        print("stop: terminate orchestrator via SIGINT or kill pid")
    else:
        usage()
