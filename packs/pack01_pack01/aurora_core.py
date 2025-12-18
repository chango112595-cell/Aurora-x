#!/usr/bin/env python3
"""
packs/pack01_pack01/aurora_core.py
Unified Process Core - event bus, lifecycle, logging, state store
Safe: operates only in pack folder, no network binds.
"""
import sys, os, time, signal
from pathlib import Path
ROOT = Path(__file__).resolve().parent
# local imports
from eventbus import EventBus
from logger import get_logger
from state_store import StateStore

LOG = get_logger(ROOT / "logs" / "pack01.log")
BUS = EventBus()
STATE = StateStore(ROOT / "data" / "state.json")

RUN = True

def _signal(sig, frame):
    global RUN
    LOG.info("Signal received, shutting down")
    RUN = False

signal.signal(signal.SIGINT, _signal)
signal.signal(signal.SIGTERM, _signal)

def main():
    LOG.info("Aurora Unified Core starting")
    # simple startup sequence
    STATE.set("started_at", time.time())
    BUS.publish("system.start", {"ts": time.time()})
    # minimal service loop - responds to simple events
    while RUN:
        try:
            # process bus events if any (non-blocking)
            ev = BUS.poll(timeout=0.1)
            if ev:
                LOG.info(f"Processed event: {ev['topic']}")
                # simple example: if event requests state update
                if ev["topic"] == "state.set":
                    STATE.set(ev["data"].get("k"), ev["data"].get("v"))
        except Exception as e:
            LOG.exception("Main loop exception: %s", e)
        time.sleep(0.05)
    # shutdown
    BUS.publish("system.stop", {"ts": time.time()})
    LOG.info("Aurora Unified Core stopped")

if __name__ == "__main__":
    main()
