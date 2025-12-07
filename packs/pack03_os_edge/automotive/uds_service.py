#!/usr/bin/env python3
"""
UDS (Unified Diagnostic Services) helper
- High-level wrappers to read vehicle information
- Does NOT perform critical writes; writes are suggestions saved to disk for human approval
Requires python-can + udsoncan for full functionality
"""

import os, json, time
SUGGEST_DIR = "automotive/suggestions"

try:
    import can
    from udsoncan.client import Client
    from udsoncan.connections import PythonIsoTpConnection
    UDS_OK = True
except Exception:
    UDS_OK = False

def read_vin():
    if not UDS_OK:
        return {"vin": "SIM-VIN-000", "note":"udsoncan not installed"}
    # implement with python-can + isotp (this is device-specific)
    return {"vin":"REAL-VIN-PLACEHOLDER"}

def request_ecu_action(ecu, action, payload):
    # Save suggestion; require human signature/approval before execution
    os.makedirs(SUGGEST_DIR, exist_ok=True)
    ts = int(time.time()*1000)
    fn = os.path.join(SUGGEST_DIR, f"uds_suggest_{ts}.json")
    with open(fn,"w") as fh:
        json.dump({"ecu":ecu,"action":action,"payload":payload,"ts":time.time()}, fh, indent=2)
    return {"ok":True,"file":fn}
