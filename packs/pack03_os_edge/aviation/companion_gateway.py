#!/usr/bin/env python3
"""
Companion computer gateway for aviation.
- Connects to flight computer via permitted, certified interface (MAVLink or ARINC-429 gateway)
- Collects telemetry, stores suggestions, prepares uplink packages (requires human sign-off)
- Does NOT perform auto-flight-critical modifications
"""

import json
import time
from pathlib import Path

SUGGEST_DIR = Path("aviation/suggestions")
SUGGEST_DIR.mkdir(parents=True, exist_ok=True)


def collect_telemetry(allow_sim: bool = False):
    """
    Collect telemetry from autopilot. When allow_sim=True, returns static sample;
    otherwise raises until a real interface is provided.
    """
    if not allow_sim:
        raise RuntimeError(
            "Autopilot telemetry not configured; enable hardware integration or allow_sim."
        )
    return {"airspeed": 123, "alt": 1000, "gps": [39.0, -86.0], "mode": "simulated"}


def prepare_uplink(commands, manifest):
    ts = int(time.time())
    pkg = SUGGEST_DIR / f"uplink_{ts}.json"
    payload = {"ts": time.time(), "commands": commands, "manifest": manifest}
    pkg.write_text(json.dumps(payload, indent=2))
    print("Saved uplink package:", pkg)
    return pkg


if __name__ == "__main__":
    print("Aviation companion gateway running. Ctrl-C to stop.")
    while True:
        telemetry = collect_telemetry()
        print("telemetry:", telemetry)
        time.sleep(5)
