#!/usr/bin/env python3
"""
Stub to send uplink via certified ground station.
Note: Satellite uplink must go through certified ground station uplink chain;
this is only companion-side tooling.
"""

import json, time
from pathlib import Path

def send_uplink(pkg_path, ground_station_url=None):
    print(f"STUB: Would send {pkg_path} to ground station")
    print("In production: use certified ground station API")
    return {"status": "stub", "pkg": str(pkg_path)}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        send_uplink(sys.argv[1])
    else:
        print("Usage: send_uplink_stub.py <package_path>")
