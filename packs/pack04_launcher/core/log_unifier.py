#!/usr/bin/env python3
"""
log_unifier.py - collects logs from packs and provides unified append-only files.
Designed to be safe and local-only.
"""

import json
import time
from pathlib import Path


class LogUnifier:
    def __init__(self, path=None):
        if path is None:
            path = Path(__file__).resolve().parents[1] / "logs" / "unified.log"
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, source, line):
        entry = {"ts": time.time(), "source": source, "line": line}
        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def tail(self, n=100):
        if not self.path.exists():
            return []
        with open(self.path) as f:
            lines = f.readlines()[-n:]
        return [json.loads(l) for l in lines if l.strip()]

    def clear(self):
        if self.path.exists():
            self.path.unlink()
