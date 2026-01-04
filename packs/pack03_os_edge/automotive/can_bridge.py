#!/usr/bin/env python3
"""
CAN Bridge - Companion-computer pattern
- Reads CAN bus via python-can (socketcan or serial)
- Publishes telemetry to Aurora Core via local AuroraLink (UDP/TCP)
- Stores 'suggestions' into suggestions/ for human approval
- Does NOT send critical commands automatically
"""

import os, json, time, threading
from pathlib import Path

AURORA_TOKEN = os.environ.get("AURORA_API_TOKEN", "aurora-dev-token")
SUGGEST_DIR = Path("automotive/suggestions"); SUGGEST_DIR.mkdir(parents=True, exist_ok=True)
USE_CAN = True

# try import python-can; if missing, run in simulated mode
try:
    import can
    CAN_AVAILABLE = True
except Exception:
    CAN_AVAILABLE = False

def read_loop(interface='can0', channel=None, bustype='socketcan'):
    if not CAN_AVAILABLE:
        # simulation mode: emit fake telemetry
        i = 0
        while True:
            msg = {"timestamp": time.time(), "frame": "0x100", "data": [i%256]}
            publish_telemetry(msg)
            i += 1
            time.sleep(1)
    else:
        bus = can.interface.Bus(channel=interface, bustype=bustype)
        for msg in bus:
            publish_telemetry({"timestamp": time.time(), "arbitration_id": msg.arbitration_id, "data": list(msg.data)})

def publish_telemetry(msg):
    # Naive UDP to local AuroraLink hub on 9801 (Aurora Core)
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(json.dumps({"type":"can_telemetry","payload": msg}).encode(), ("127.0.0.1", 9801))
    except Exception:
        pass

def store_suggestion(data):
    ts = int(time.time()*1000)
    fn = SUGGEST_DIR / f"suggestion_{ts}.json"
    fn.write_text(json.dumps(data, indent=2))
    print("Saved suggestion:", fn)

def suggest_ecu_command(ecu, service, params, reason):
    # prepare non-destructive suggestion; human must approve
    obj = {"ecu":ecu,"service":service,"params":params,"reason":reason,"ts":time.time()}
    store_suggestion(obj)
    return {"ok":True, "saved": True}

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--interface", default="can0")
    p.add_argument("--bustype", default="socketcan")
    args = p.parse_args()
    read_loop(interface=args.interface, bustype=args.bustype)
