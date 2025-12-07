#!/usr/bin/env python3
"""
NMEA2000 placeholder - needs specific hardware (CAN-to-NMEA2000 interface)
For NMEA2000 you'll need a CAN-to-NMEA2000 interface (e.g., CAN transceiver with Seatalk/NMEA2000 stack).
Use companion computer.
"""

import time

def nmea2000_loop():
    print("NMEA2000 stub - requires CAN-to-NMEA2000 hardware interface")
    while True:
        print("NMEA2000 SIM: waiting for hardware...")
        time.sleep(5)

if __name__ == "__main__":
    nmea2000_loop()
