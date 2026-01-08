#!/usr/bin/env python3
"""
UDS (Unified Diagnostic Services) helper
- High-level wrappers to read vehicle information
- Does NOT perform critical writes; writes are suggestions saved to disk for human approval
Requires python-can + udsoncan for full functionality
"""

import json
import os
import time

SUGGEST_DIR = "automotive/suggestions"

try:
    from udsoncan.client import Client
    from udsoncan.connections import PythonIsoTpConnection

    UDS_OK = True
except Exception:
    UDS_OK = False


def read_vin(bus=None):
    """
    Read VIN from vehicle. Requires udsoncan + hardware; will not emit fake VINs.
    Optionally accepts a pre-configured bus/session for testing.
    """
    if not UDS_OK:
        raise RuntimeError("udsoncan not installed; cannot read VIN without dependencies.")

    if bus is None:
        raise RuntimeError("No CAN/UDS session provided; supply a bus/session to read VIN.")

    try:
        client = Client(PythonIsoTpConnection(bus), request_timeout=2)
        with client:
            resp = client.read_data_by_identifier(0xF190)
            return {"vin": resp.data.decode(errors="ignore").strip()}
    except Exception as exc:
        raise RuntimeError(f"VIN read failed: {exc}") from exc


def request_ecu_action(ecu, action, payload):
    # Save suggestion; require human signature/approval before execution
    os.makedirs(SUGGEST_DIR, exist_ok=True)
    ts = int(time.time() * 1000)
    fn = os.path.join(SUGGEST_DIR, f"uds_suggest_{ts}.json")
    with open(fn, "w") as fh:
        json.dump(
            {"ecu": ecu, "action": action, "payload": payload, "ts": time.time()}, fh, indent=2
        )
    return {"ok": True, "file": fn}
