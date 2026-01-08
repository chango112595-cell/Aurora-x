#!/usr/bin/env python3
import json
import os
import tempfile
from pathlib import Path


class StateStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({}))

    def _write_atomic(self, data):
        tmp = tempfile.NamedTemporaryFile(delete=False, dir=str(self.path.parent))
        try:
            tmp.write(json.dumps(data, indent=2).encode())
            tmp.flush()
            tmp.close()
            os.replace(tmp.name, str(self.path))
        finally:
            if os.path.exists(tmp.name):
                try:
                    os.remove(tmp.name)
                except Exception:
                    pass

    def get(self, key, default=None):
        try:
            d = json.loads(self.path.read_text())
            return d.get(key, default)
        except Exception:
            return default

    def set(self, key, value):
        d = {}
        try:
            d = json.loads(self.path.read_text())
        except Exception:
            d = {}
        d[key] = value
        self._write_atomic(d)
        return True
