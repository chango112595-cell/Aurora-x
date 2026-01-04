import json
import time
from pathlib import Path


class AuroraBridge:
    def __init__(self, aurora_nexus_path=None):
        self.aurora_path = Path(aurora_nexus_path) if aurora_nexus_path else None
        self.connected = False
        self.event_log = []

    def connect(self, path=None):
        if path:
            self.aurora_path = Path(path)
        if self.aurora_path and self.aurora_path.exists():
            self.connected = True
            self._log_event("connected", {"path": str(self.aurora_path)})
            return True
        return False

    def _log_event(self, event_type, details=None):
        self.event_log.append(
            {"type": event_type, "details": details or {}, "timestamp": time.time()}
        )

    def send_incident(self, incident):
        if not self.connected:
            return False
        incidents_dir = self.aurora_path / "incidents"
        incidents_dir.mkdir(parents=True, exist_ok=True)
        incident_id = f"INC-{int(time.time() * 1000)}"
        incident["id"] = incident_id
        path = incidents_dir / f"{incident_id}.json"
        with open(path, "w") as f:
            json.dump(incident, f, indent=2)
        self._log_event("incident_sent", {"id": incident_id})
        return True

    def fetch_modules(self, category=None):
        if not self.connected:
            return []
        modules_dir = self.aurora_path / "modules"
        if not modules_dir.exists():
            return []
        modules = []
        for p in modules_dir.glob("**/*.py"):
            if category is None or category in str(p):
                modules.append(str(p))
        return modules

    def push_module(self, module_path, target_category):
        if not self.connected:
            return False
        src = Path(module_path)
        if not src.exists():
            return False
        target_dir = self.aurora_path / "modules" / target_category
        target_dir.mkdir(parents=True, exist_ok=True)
        import shutil

        shutil.copy2(src, target_dir / src.name)
        self._log_event("module_pushed", {"src": str(src), "category": target_category})
        return True

    def sync_registry(self):
        if not self.connected:
            return {"synced": False}
        registry_path = self.aurora_path / "registry" / "modules_registry.json"
        if registry_path.exists():
            with open(registry_path) as f:
                return {"synced": True, "registry": json.load(f)}
        return {"synced": False, "error": "Registry not found"}

    def get_status(self):
        return {
            "connected": self.connected,
            "path": str(self.aurora_path) if self.aurora_path else None,
            "events": len(self.event_log),
        }
