"""
Plugin registry - record installed plugins, metadata, status.
Registry persisted under data/plugins/registry.json
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "data" / "plugins" / "registry.json"
REG.parent.mkdir(parents=True, exist_ok=True)
if not REG.exists():
    REG.write_text(json.dumps({}))


class PluginRegistry:
    def __init__(self):
        self._path = REG

    def list(self):
        return json.loads(self._path.read_text())

    def register(self, manifest: dict, files: list):
        d = self.list()
        plugin_id = manifest["id"]
        d[plugin_id] = {
            "manifest": manifest,
            "files": files,
            "installed_at": __import__("time").time(),
            "enabled": False,
        }
        self._path.write_text(json.dumps(d, indent=2))
        return True

    def get(self, plugin_id):
        return self.list().get(plugin_id)

    def enable(self, plugin_id):
        d = self.list()
        if plugin_id in d:
            d[plugin_id]["enabled"] = True
            self._path.write_text(json.dumps(d, indent=2))
            return True
        return False

    def disable(self, plugin_id):
        d = self.list()
        if plugin_id in d:
            d[plugin_id]["enabled"] = False
            self._path.write_text(json.dumps(d, indent=2))
            return True
        return False

    def unregister(self, plugin_id):
        d = self.list()
        if plugin_id in d:
            del d[plugin_id]
            self._path.write_text(json.dumps(d, indent=2))
            return True
        return False
