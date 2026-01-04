#!/usr/bin/env python3
"""
NMEA 0183 bridge: read from serial or TCP, emit parsed lines to Aurora core.
pip install pynmea2
"""

import os, serial, time, json
from pathlib import Path

try:
    import pynmea2
except Exception:
    pynmea2 = None

PORT = os.environ.get("NMEA_PORT", "/dev/ttyUSB0")
BAUD = int(os.environ.get("NMEA_BAUD", "4800"))

def read_loop():
    if not pynmea2:
        print("pynmea2 not installed; simulate")
        while True:
            print("SIM NMEA")
            time.sleep(2)
    else:
        with serial.Serial(PORT, BAUD, timeout=1) as ser:
            while True:
                line = ser.readline().decode(errors="ignore").strip()
                if not line: continue
                try:
                    msg = pynmea2.parse(line)
                    print("NMEA:", msg)
                except Exception:
                    pass

if __name__ == "__main__":
    read_loop()
