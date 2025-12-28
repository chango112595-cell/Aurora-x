#!/usr/bin/env python3
"""
CAN Bridge - Companion-computer pattern
- Reads CAN bus via python-can (socketcan or serial)
- Publishes telemetry to Aurora Core via local AuroraLink (UDP/TCP)
- Stores 'suggestions' into suggestions/ for human approval
- Does NOT send critical commands automatically
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Optional

from aurora_x.config.runtime_config import data_path

_logger = logging.getLogger("aurora.can_bridge")

AURORA_TOKEN = os.environ.get("AURORA_API_TOKEN", "aurora-dev-token")
SUGGEST_DIR = data_path("automotive", "suggestions")
SUGGEST_DIR.mkdir(parents=True, exist_ok=True)

# Try import python-can; if missing, functionality is unavailable
try:
    import can
    CAN_AVAILABLE = True
except ImportError:
    CAN_AVAILABLE = False
    _logger.warning("python-can not installed - CAN bridge unavailable")


def read_loop(interface: str = 'can0', channel: Optional[str] = None, bustype: str = 'socketcan'):
    """Main CAN bus read loop.

    Args:
        interface: CAN interface name
        channel: Optional channel override
        bustype: CAN bus type (socketcan, serial, etc.)
    """
    if not CAN_AVAILABLE:
        _logger.error("Cannot start CAN read loop: python-can not installed")
        _logger.info("Install with: pip install python-can")
        _logger.info(
            "CAN bridge will not emit data until python-can is available")
        # Do NOT emit fake data - just log and return
        return

    try:
        bus = can.interface.Bus(channel=interface, bustype=bustype)
        _logger.info(f"CAN bridge started on {interface} ({bustype})")
        for msg in bus:
            publish_telemetry({
                "timestamp": time.time(),
                "arbitration_id": msg.arbitration_id,
                "data": list(msg.data)
            })
    except Exception as e:
        _logger.error(f"CAN bus error: {e}")


def publish_telemetry(msg: dict) -> bool:
    """Publish telemetry to Aurora Core via UDP.

    Args:
        msg: Telemetry message dict

    Returns:
        True if sent successfully, False otherwise.
    """
    import socket
    try:
        aurora_host = os.environ.get("AURORA_HOST", "127.0.0.1")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(json.dumps({"type": "can_telemetry",
                 "payload": msg}).encode(), (aurora_host, 9801))
        return True
    except Exception as e:
        _logger.debug(f"Failed to publish telemetry: {e}")
        return False


def store_suggestion(data):
    ts = int(time.time()*1000)
    fn = SUGGEST_DIR / f"suggestion_{ts}.json"
    fn.write_text(json.dumps(data, indent=2))
    print("Saved suggestion:", fn)


def suggest_ecu_command(ecu, service, params, reason):
    # prepare non-destructive suggestion; human must approve
    obj = {"ecu": ecu, "service": service, "params": params,
           "reason": reason, "ts": time.time()}
    store_suggestion(obj)
    return {"ok": True, "saved": True}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--interface", default="can0")
    p.add_argument("--bustype", default="socketcan")
    args = p.parse_args()
    read_loop(interface=args.interface, bustype=args.bustype)
