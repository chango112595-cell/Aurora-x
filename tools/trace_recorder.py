#!/usr/bin/env python3
"""
Trace recorder for agent runs and memory interactions.
Saves chronological JSON traces you can replay later for debugging/simulation.
"""

import json
import time
from pathlib import Path

TRACE_DIR = Path(".traces")
TRACE_DIR.mkdir(exist_ok=True)


def record(trace_obj):
    t = int(time.time() * 1000)
    Path(TRACE_DIR / f"trace_{t}.json").write_text(json.dumps(trace_obj, indent=2))


def load(trace_path):
    return json.loads(Path(trace_path).read_text())
