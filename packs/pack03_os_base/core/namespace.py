"""
Namespace registry: simple in-process registry that maps pack ids to runtime metadata.
Used by the scheduler and the VFS to isolate pack resources.
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "data" / "namespaces.json"
REG.parent.mkdir(parents=True, exist_ok=True)
if not REG.exists():
    REG.write_text(json.dumps({}))

class NamespaceRegistry:
    def __init__(self):
        self._path = REG

    def list(self):
        return json.loads(self._path.read_text())

    def register(self, pack_id: str, meta: dict):
        d = self.list()
        d[pack_id] = meta
        self._path.write_text(json.dumps(d, indent=2))
        return True

    def get(self, pack_id: str):
        return self.list().get(pack_id)

    def unregister(self, pack_id: str):
        d = self.list()
        if pack_id in d:
            del d[pack_id]
            self._path.write_text(json.dumps(d, indent=2))
            return True
        return False
