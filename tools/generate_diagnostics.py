#!/usr/bin/env python3
"""
Quick script to generate diagnostic data
Run this BEFORE starting the diagnostic server
"""
import json
import socket
from datetime import datetime
from pathlib import Path

PORTS = {
    5000: "Aurora UI (frontend)",
    5001: "Aurora backend (uvicorn)",
    5002: "Learning API / FastAPI",
    8080: "File Server",
    8000: "Standalone dashboards (legacy)",
}

DIAGNOSTICS_FILE = Path(__file__).parent / "tools" / "diagnostics.json"


def check_port(port, host="127.0.0.1", timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except:
        return False


def generate_diagnostics():
    """Generate and save diagnostic report"""
    report = {"timestamp": datetime.now().isoformat(), "services": {}}

    print(f"\n{'='*70}")
    print("[DATA] GENERATING AURORA DIAGNOSTICS")
    print(f"{'='*70}\n")

    for port, name in PORTS.items():
        up = check_port(port)
        status = "UP" if up else "DOWN"
        icon = "[OK]" if up else "[ERROR]"

        print(f"{icon} [PORT {port}] {name}: {status}")

        report["services"][port] = {"name": name, "port": port, "status": status, "url": f"http://127.0.0.1:{port}"}

    print(f"\n{'='*70}\n")

    # Save report
    with open(DIAGNOSTICS_FILE, "w") as f:
        json.dump(report, f, indent=2)

    print(f"[OK] Diagnostic data saved to: {DIAGNOSTICS_FILE}\n")
    return report


if __name__ == "__main__":
    generate_diagnostics()
