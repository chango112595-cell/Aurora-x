#!/usr/bin/env python3
"""
Simple AIS ingest example. In production, use libais or dedicated AIS receivers.
"""

import random
import time


def simulate_ais():
    while True:
        print("AIS: MMSI", random.randint(200000000, 799999999))
        time.sleep(3)


if __name__ == "__main__":
    simulate_ais()
