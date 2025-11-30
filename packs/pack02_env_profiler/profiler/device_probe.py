#!/usr/bin/env python3
"""
Lightweight device probe. Safe by default (--safe).
Outputs basic device info JSON to stdout.
"""
import argparse, platform, json, shutil, os, sys, subprocess
from pathlib import Path
def probe_basic():
    return {
        "platform": platform.system(),
        "platform_lower": platform.system().lower(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "cores": os.cpu_count(),
        "has_node": bool(shutil.which("node")),
        "has_python3": bool(shutil.which("python3") or shutil.which("python")),
    }

def probe_os_details():
    info = {}
    if platform.system().lower() == "linux":
        try:
            with open("/proc/cpuinfo") as f:
                cpu = f.read()
            info["cpuinfo_snippet"] = cpu.splitlines()[:8]
        except Exception:
            info["cpuinfo_snippet"] = []
    return info

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--safe", action="store_true", help="Run safe probe (default behavior).")
    p.add_argument("--out", default=None, help="Write output to path")
    args = p.parse_args()
    out = {"basic": probe_basic(), "details": probe_os_details()}
    txt = json.dumps(out, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(txt)
    else:
        print(txt)

if __name__ == "__main__":
    main()
