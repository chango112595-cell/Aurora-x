#!/usr/bin/env python3
"""
NMEA2000 adapter safety wrapper.

In production, this module should only be used when a CAN-to-NMEA2000 interface
is available. Without hardware, it runs in explicit "safe-sim" mode and refuses
to emit bogus data.
"""

import time
from typing import Optional


class NMEA2000Adapter:
    """Minimal, hardware-gated adapter for NMEA2000."""

    def __init__(self, device: Optional[str] = None, simulated: bool = False):
        self.device = device
        self.simulated = simulated or not bool(device)

    def connect(self) -> None:
        if self.simulated:
            raise RuntimeError(
                "NMEA2000 hardware not configured. Provide device path to enable live mode."
            )
        # Real hardware integration would go here (e.g., python-can / CAN transceiver init).

    def read_once(self) -> dict:
        if self.simulated:
            return {"status": "simulated", "message": "NMEA2000 hardware not connected"}
        return {"status": "ok", "ts": time.time()}


def nmea2000_loop(device: Optional[str] = None):
    adapter = NMEA2000Adapter(device=device, simulated=not bool(device))
    try:
        adapter.connect()
    except RuntimeError as err:
        print(f"[NMEA2000] {err}")
        return

    while True:
        print(adapter.read_once())
        time.sleep(1)


if __name__ == "__main__":
    nmea2000_loop()
