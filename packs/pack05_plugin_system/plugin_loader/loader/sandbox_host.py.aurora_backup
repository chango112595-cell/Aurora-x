#!/usr/bin/env python3
"""
sandbox_host.py - long-running host process that listens for run requests.
For simplicity this implementation polls a requests directory (data/requests) for
JSON request files containing {"plugin": "...", "cmd": "..."} and writes result files.
This avoids network dependencies and is safe for unit tests.
"""

import time, json, os
from pathlib import Path
from .sandbox_runtime import SandboxRuntime
REQ_DIR = Path(__file__).resolve().parents[1] / "data" / "requests"
RES_DIR = Path(__file__).resolve().parents[1] / "data" / "responses"
REQ_DIR.mkdir(parents=True, exist_ok=True)
RES_DIR.mkdir(parents=True, exist_ok=True)

def _process_file(p: Path):
    try:
        obj = json.loads(p.read_text())
        plugin = obj.get("plugin")
        cmd = obj.get("cmd")
        sr = SandboxRuntime(plugin)
        res = sr.run_entry(cmd, timeout=obj.get("timeout", 10))
        outp = {"req": p.name, "result": res}
        (RES_DIR / (p.name + ".result.json")).write_text(json.dumps(outp, indent=2))
    except Exception as e:
        (RES_DIR / (p.name + ".error.json")).write_text(json.dumps({"error": str(e)}))
    finally:
        try:
            p.unlink()
        except Exception:
            pass

def main_loop(poll_interval=0.5):
    while True:
        for f in list(REQ_DIR.iterdir()):
            if f.is_file() and f.suffix == ".req":
                _process_file(f)
        time.sleep(poll_interval)

if __name__ == "__main__":
    main_loop()
