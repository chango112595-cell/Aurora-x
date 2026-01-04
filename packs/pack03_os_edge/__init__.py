"""
Aurora Pack 03: OS Base + EdgeOS Runtimes (Unified)

This pack consolidates the OS layer and all EdgeOS runtimes:
- 3A: OS Base - Core operating system layer
- 3B: Automotive - CAN/UDS/OBD-II bridge, ECU workflows
- 3C: Aviation - RTOS partitioning, companion gateway
- 3D: Maritime - NMEA2000/NMEA0183/AIS bridge
- 3E: IoT - ESP32 MicroPython, OTA updates
- 3F: Router - OpenWRT/EdgeOS agent
- 3G: Satellite - Ground uplink, companion agent
- 3H: Smart TV - Android TV/WebOS/Tizen agents
- 3I: Mobile - Android/iOS companion, Termux
- 3J: Cross-Build - Multi-arch tooling, firmware packaging

Author: Aurora AI System
Version: 1.0.0
Mode: Offline (default) or Cloud-assisted via AURORA_MODE env var
"""

import os
from pathlib import Path

PACK_ID = "pack03"
PACK_NAME = "OS Base + EdgeOS Runtimes"
PACK_VERSION = "1.0.0"

AURORA_MODE = os.environ.get("AURORA_MODE", "offline")

SUBMODULES = {
    "3A": {"name": "os_base", "desc": "Core OS layer"},
    "3B": {"name": "automotive", "desc": "CAN/UDS/OBD-II bridge"},
    "3C": {"name": "aviation", "desc": "RTOS partitioning"},
    "3D": {"name": "maritime", "desc": "NMEA2000/AIS bridge"},
    "3E": {"name": "iot", "desc": "ESP32 MicroPython"},
    "3F": {"name": "router", "desc": "OpenWRT/EdgeOS"},
    "3G": {"name": "satellite", "desc": "Ground uplink"},
    "3H": {"name": "tv", "desc": "Smart TV agents"},
    "3I": {"name": "mobile", "desc": "Android/iOS"},
    "3J": {"name": "build", "desc": "Cross-build tooling"},
}


def get_pack_info():
    """Return pack metadata"""
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "version": PACK_VERSION,
        "mode": AURORA_MODE,
        "submodules": {k: v["name"] for k, v in SUBMODULES.items()},
        "total_submodules": len(SUBMODULES),
        "status": "integrated",
    }


def load_all_runtimes():
    """Load all EdgeOS runtimes"""
    loaded = {}
    base_path = Path(__file__).parent

    for code, info in SUBMODULES.items():
        runtime_path = base_path / info["name"]
        py_files = list(runtime_path.glob("**/*.py")) if runtime_path.exists() else []
        loaded[code] = {
            "name": info["name"],
            "description": info["desc"],
            "status": "loaded" if py_files else "empty",
            "files": len(py_files),
            "path": str(runtime_path),
        }

    return loaded


def get_runtime(code: str):
    """Get a specific EdgeOS runtime by code (e.g., '3B' for automotive)"""
    if code not in SUBMODULES:
        return None
    return SUBMODULES[code]
