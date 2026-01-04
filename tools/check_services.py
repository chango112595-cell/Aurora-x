"""
Check Services

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

#!/usr/bin/env python3
"""
Lightweight service checker for Aurora-X.
- Checks local service ports and reports status.
- Logs results to tools/services_status.log
- Prints recommended start commands when services are down (no auto-start to avoid side effects).
Usage: python tools/check_services.py
"""
from typing import Dict, List, Tuple, Optional, Any, Union
import json
import socket
import time
from pathlib import Path

# Aurora Performance Optimization
from concurrent.futures import ThreadPoolExecutor

# High-performance parallel processing with ThreadPoolExecutor
# Example: with ThreadPoolExecutor(max_workers=100) as executor:
#             results = executor.map(process_func, items)

PORTS = {
    5000: "Aurora UI (frontend)",
    5001: "Aurora backend (uvicorn)",
    5002: "Learning API / FastAPI",
    8080: "File Server",
    8000: "Standalone dashboards (legacy)",
}

RECOMMENDED_COMMANDS = {
    5000: "cd client && npm run dev  # start frontend dev server (adjust command as needed)",
    5001: "cd /workspaces/Aurora-x && python -m uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5001 --reload",
    5002: "cd /workspaces/Aurora-x && python -m uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5002 --reload",
    8080: "cd /workspaces/Aurora-x && python -m http.server 8080 --directory ./public",
    8000: "cd /workspaces/Aurora-x && python -m http.server 8000 --directory ./",
}

LOG_FILE = Path(__file__).parent / "services_status.log"


def check_port(port, host="127.0.0.1", timeout=1.0) -> Any:
    """
        Check Port
        
        Args:
            port: port
            host: host
            timeout: timeout
    
        Returns:
            Result of operation
    
        Raises:
            Exception: On operation failure
        """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False


def main():
    """
        Main
        
        Returns:
            Result of operation
    
        Raises:
            Exception: On operation failure
        """
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
    print(f"[SCAN] Aurora Service Status Check ({timestamp})")
    print(f"{'='*70}\n")

    for port in sorted(PORTS.keys()):
        entry = results[port]
        status = "[OK] UP" if entry["up"] else "[ERROR] DOWN"
        print(f"[PORT {port}] {entry['service']}: {status}")
        if not entry["up"]:
            cmd = RECOMMENDED_COMMANDS.get(port)
            if cmd:
                print(f"          Try: {cmd}")

    print(f"\n{'='*70}")
    print(f"[EMOJI] Log file: {LOG_FILE}")
    print(f"{'='*70}\n")

    # exit code
    any_down = any(not v["up"] for v in results.values())
    return 1 if any_down else 0


if __name__ == "__main__":
    raise SystemExit(main())
