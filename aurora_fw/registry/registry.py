#!/usr/bin/env python3
"""
Local firmware registry:
- Store metadata about available firmware images (axf)
- Query by target, version, channel (stable/canary)
"""

import json
import time
from pathlib import Path

REG_DIR = Path(".fw_registry")
REG_DIR.mkdir(exist_ok=True)


def register(axf_path: str, channel="stable", meta=None):
    p = Path(axf_path)
    if not p.exists():
        raise FileNotFoundError(axf_path)
    rec = {"path": str(p), "channel": channel, "meta": meta or {}, "ts": time.time()}
    idx = REG_DIR / (p.stem + ".json")
    idx.write_text(json.dumps(rec, indent=2))
    return rec


def list_registry():
    return [json.loads(p.read_text()) for p in REG_DIR.glob("*.json")]
