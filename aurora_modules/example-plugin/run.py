#!/usr/bin/env python3
import time, os, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
log = ROOT / "aurora_logs" / "example-plugin.out.log"
log.parent.mkdir(parents=True, exist_ok=True)

def main():
    i = 0
    with open(log, "a") as fh:
        while True:
            fh.write(f"{__name__} alive {i}\n")
            fh.flush()
            i += 1
            time.sleep(5)

if __name__ == "__main__":
    main()
