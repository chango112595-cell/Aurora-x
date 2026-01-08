#!/usr/bin/env python3
"""
metrics.py - Simple metrics recording for jobs and supervisor events.
Writes a small JSON metrics file and exposes in-memory quick API.
"""

import json
import time
from pathlib import Path


class Metrics:
    def __init__(self, path=None):
        if path is None:
            path = Path(__file__).resolve().parents[1] / "data" / "metrics.json"
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"records": []}))

    def record(self, job, rc):
        d = json.loads(self.path.read_text())
        d["records"].append({"job": job, "rc": rc, "ts": time.time()})
        self.path.write_text(json.dumps(d, indent=2))

    def last_rc(self, job):
        d = json.loads(self.path.read_text())
        for r in reversed(d.get("records", [])):
            if r.get("job") == job:
                return r.get("rc")
        return None

    def all_records(self):
        d = json.loads(self.path.read_text())
        return d.get("records", [])
