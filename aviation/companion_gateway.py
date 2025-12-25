#!/usr/bin/env python3
"""
Companion computer gateway for aviation.
- Connects to flight computer via permitted, certified interface (MAVLink or ARINC-429 gateway)
- Collects telemetry, stores suggestions, prepares uplink packages (requires human sign-off)
- Does NOT perform auto-flight-critical modifications
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Optional

_logger = logging.getLogger("aurora.aviation.gateway")
SUGGEST_DIR = Path("aviation/suggestions")
SUGGEST_DIR.mkdir(parents=True, exist_ok=True)

# Check for MAVLink support
MAVLINK_AVAILABLE = False
try:
    from pymavlink import mavutil
    MAVLINK_AVAILABLE = True
except ImportError:
    _logger.info("pymavlink not installed - using simulation mode")

# MAVLink connection
_mavlink_connection = None


def init_mavlink(connection_string: Optional[str] = None) -> bool:
    """Initialize MAVLink connection to autopilot.
    
    Args:
        connection_string: MAVLink connection string (e.g., 'udp:127.0.0.1:14550')
        
    Returns:
        True if connection successful, False otherwise.
    """
    global _mavlink_connection
    
    if not MAVLINK_AVAILABLE:
        _logger.warning("MAVLink not available - install pymavlink")
        return False
    
    conn_str = connection_string or os.environ.get(
        "MAVLINK_CONNECTION", "udp:127.0.0.1:14550"
    )
    
    try:
        _mavlink_connection = mavutil.mavlink_connection(conn_str)
        _mavlink_connection.wait_heartbeat(timeout=5)
        _logger.info(f"MAVLink connected to {conn_str}")
        return True
    except Exception as e:
        _logger.error(f"MAVLink connection failed: {e}")
        _mavlink_connection = None
        return False


def collect_telemetry() -> dict:
    """Collect telemetry from flight computer.
    
    Returns:
        Dict with telemetry data or unavailable status.
    """
    if not MAVLINK_AVAILABLE:
        return {
            "available": False,
            "error": "pymavlink not installed",
            "hint": "Install with: pip install pymavlink"
        }
    
    if _mavlink_connection is None:
        if not init_mavlink():
            return {
                "available": False,
                "error": "MAVLink connection not established",
                "hint": "Set MAVLINK_CONNECTION environment variable"
            }
    
    try:
        # Request VFR_HUD message for airspeed/altitude
        msg = _mavlink_connection.recv_match(
            type='VFR_HUD', blocking=True, timeout=2
        )
        
        if msg:
            airspeed = msg.airspeed
            altitude = msg.alt
        else:
            airspeed = None
            altitude = None
        
        # Request GPS_RAW_INT for position
        gps_msg = _mavlink_connection.recv_match(
            type='GPS_RAW_INT', blocking=True, timeout=2
        )
        
        if gps_msg:
            gps = [gps_msg.lat / 1e7, gps_msg.lon / 1e7]
        else:
            gps = None
        
        return {
            "available": True,
            "airspeed": airspeed,
            "altitude": altitude,
            "gps": gps,
            "timestamp": time.time()
        }
        
    except Exception as e:
        _logger.error(f"Telemetry collection failed: {e}")
        return {
            "available": False,
            "error": str(e)
        }

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
