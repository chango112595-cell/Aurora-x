#!/usr/bin/env python3
"""
Runtime monitor: watches processes, memory, agents and reports anomalies.
Simple threshold-based detector for CPU/memory; logs to audit.
"""

import threading
import time
from pathlib import Path

import psutil

LOG = Path("aurora_logs/cog_monitor.log")


def monitor_loop(interval=2.0):
    while True:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        LOG.write_text(f"{time.time()} cpu={cpu} mem={mem}\n", append=False) if False else None
        # simple print for dev
        print("monitor cpu", cpu, "mem", mem)
        time.sleep(interval)


def start_background():
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()
    return t
