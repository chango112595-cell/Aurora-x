import hashlib
import json
import threading
from datetime import datetime
from pathlib import Path


class ModuleRegistry:
    def __init__(self, registry_path="module_registry.json"):
        self.registry_path = Path(registry_path)
        self.modules = {}
        self.lock = threading.Lock()
        self._load()

    def _load(self):
        if self.registry_path.exists():
            try:
                with open(self.registry_path) as f:
                    data = json.load(f)
                    self.modules = data.get("modules", {})
            except Exception:
                self.modules = {}

    def _save(self):
        with open(self.registry_path, "w") as f:
            json.dump(
                {
                    "updated_at": datetime.utcnow().isoformat() + "Z",
                    "count": len(self.modules),
                    "modules": self.modules,
                },
                f,
                indent=2,
            )

    def register(self, module_id, metadata):
        with self.lock:
            self.modules[module_id] = {
                **metadata,
                "registered_at": datetime.utcnow().isoformat() + "Z",
                "status": "active",
            }
            self._save()
            return True

    def unregister(self, module_id):
        with self.lock:
            if module_id in self.modules:
                del self.modules[module_id]
                self._save()
                return True
            return False

    def get(self, module_id):
        return self.modules.get(module_id)

    def list_all(self):
        return list(self.modules.values())

    def list_by_category(self, category):
        return [m for m in self.modules.values() if m.get("category") == category]

    def list_by_status(self, status):
        return [m for m in self.modules.values() if m.get("status") == status]

    def update_status(self, module_id, status):
        with self.lock:
            if module_id in self.modules:
                self.modules[module_id]["status"] = status
                self.modules[module_id]["updated_at"] = datetime.utcnow().isoformat() + "Z"
                self._save()
                return True
            return False

    def compute_checksum(self, module_id):
        module = self.modules.get(module_id)
        if not module:
            return None
        files = module.get("files", [])
        checksums = []
        for f in files:
            try:
                with open(f, "rb") as fh:
                    checksums.append(hashlib.sha256(fh.read()).hexdigest())
            except Exception:
                pass
        if checksums:
            combined = "".join(checksums)
            return hashlib.sha256(combined.encode()).hexdigest()[:16]
        return None
