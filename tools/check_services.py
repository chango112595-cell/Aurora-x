#!/usr/bin/env python3
"""
Lightweight service checker for Aurora-X.
- Checks local service ports and reports status.
- Logs results to tools/services_status.log
- Prints recommended start commands when services are down (no auto-start to avoid side effects).
Usage: python tools/check_services.py
"""
import socket
import time
import json
from pathlib import Path

PORTS = {
    5000: "Aurora UI (frontend)",
    5001: "Aurora backend (uvicorn)",
    5002: "Learning API / FastAPI",
    8080: "File Server",
    8000: "Standalone dashboards (legacy)"
}

RECOMMENDED_COMMANDS = {
    5000: "cd client && npm run dev  # start frontend dev server (adjust command as needed)",
    5001: "cd /workspaces/Aurora-x && python -m uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5001 --reload",
    5002: "cd /workspaces/Aurora-x && python -m uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5002 --reload",
    8080: "cd /workspaces/Aurora-x && python -m http.server 8080 --directory ./public",
    8000: "cd /workspaces/Aurora-x && python -m http.server 8000 --directory ./"
}

LOG_FILE = Path(__file__).parent / "services_status.log"


def check_port(port, host="127.0.0.1", timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False


def main():
    results = {}
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    for port, label in PORTS.items():
        up = check_port(port)
        results[port] = {"service": label, "port": port, "up": up}

    # write to log
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"timestamp": timestamp, "results": results}) + "\n")

    # print summary and recommendations
    print(f"\n{'='*70}")
    print(f"🔍 Aurora Service Status Check ({timestamp})")
    print(f"{'='*70}\n")
    
    for port in sorted(PORTS.keys()):
        entry = results[port]
        status = "✅ UP" if entry["up"] else "❌ DOWN"
        print(f"[PORT {port}] {entry['service']}: {status}")
        if not entry["up"]:
            cmd = RECOMMENDED_COMMANDS.get(port)
            if cmd:
                print(f"         └─ Try: {cmd}")
    
    print(f"\n{'='*70}")
    print(f"📋 Log file: {LOG_FILE}")
    print(f"{'='*70}\n")

    # exit code
    any_down = any(not v["up"] for v in results.values())
    return 1 if any_down else 0


if __name__ == "__main__":
    raise SystemExit(main())
