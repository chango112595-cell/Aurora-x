#!/usr/bin/env python3
"""
diagnostics.py - collect small system snapshot: process counts, memory, disk usage,
and produce a compact diagnostics JSON under live/pack03_os_base/diagnostics.json
"""

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT.parents[0] / "live" / "pack03_os_base" / "diagnostics.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


def collect():
    data = {"timestamp": time.time(), "process_count": 0, "disk": {}, "env": {}}
    try:
        import psutil

        data["process_count"] = len(psutil.pids())
        disk = psutil.disk_usage(str(ROOT))
        data["disk"] = {"total": disk.total, "used": disk.used, "free": disk.free}
    except Exception:
        # fallback using os
        data["process_count"] = 0
    OUT.write_text(json.dumps(data, indent=2))
    return data


if __name__ == "__main__":
    print(collect())
