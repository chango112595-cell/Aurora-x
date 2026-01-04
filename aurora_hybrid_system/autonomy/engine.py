import json
import time
import logging
import shutil
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class IncidentHandler:
    def __init__(self, autonomy_dir):
        self.autonomy_dir = Path(autonomy_dir)
        self.incidents_dir = self.autonomy_dir / "incidents"
        self.patches_dir = self.autonomy_dir / "patches"
        self.snapshots_dir = self.autonomy_dir / "snapshots"
        for d in [self.incidents_dir, self.patches_dir, self.snapshots_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def log_incident(self, incident):
        incident_id = f"INC-{int(time.time()*1000)}"
        incident["id"] = incident_id
        incident["logged_at"] = datetime.utcnow().isoformat() + "Z"
        path = self.incidents_dir / f"{incident_id}.json"
        with open(path, 'w') as f:
            json.dump(incident, f, indent=2)
        return incident_id

    def create_snapshot(self, module_path):
        snapshot_id = f"SNAP-{int(time.time()*1000)}"
        src = Path(module_path)
        if src.exists():
            dst = self.snapshots_dir / f"{snapshot_id}_{src.name}"
            shutil.copy2(src, dst)
        return snapshot_id

    def apply_patch(self, module_path, patch):
        try:
            with open(module_path, 'r') as f:
                code = f.read()
            for replacement in patch.get("replacements", []):
                code = code.replace(replacement["old"], replacement["new"])
            with open(module_path, 'w') as f:
                f.write(code)
            return True
        except Exception as e:
            logger.error(f"Patch failed: {e}")
            return False

    def rollback(self, module_path, snapshot_id):
        try:
            snapshots = list(self.snapshots_dir.glob(f"{snapshot_id}_*"))
            if snapshots:
                shutil.copy2(snapshots[0], module_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

class RepairEngine:
    REPAIR_RULES = {
        "eval_usage": {"old": "eval(", "new": "ast.literal_eval("},
        "bare_except": {"old": "except:", "new": "except Exception:"},
        "explicit_bool_compare": [{"old": "== True", "new": ""}, {"old": "== False", "new": " is False"}]
    }

    def generate_patch(self, issues):
        replacements = []
        for issue in issues:
            pattern = issue.get("pattern") or issue.get("type")
            if pattern in self.REPAIR_RULES:
                rule = self.REPAIR_RULES[pattern]
                if isinstance(rule, list):
                    replacements.extend(rule)
                else:
                    replacements.append(rule)
        return {"replacements": replacements}

class AutonomyEngine:
    def __init__(self, autonomy_dir="aurora_autonomy"):
        self.autonomy_dir = Path(autonomy_dir)
        self.autonomy_dir.mkdir(parents=True, exist_ok=True)
        self.incident_handler = IncidentHandler(self.autonomy_dir)
        self.repair_engine = RepairEngine()
        self.audit_log = self.autonomy_dir / "audit.log"

    def _audit(self, event):
        event["timestamp"] = datetime.utcnow().isoformat() + "Z"
        with open(self.audit_log, 'a') as f:
            f.write(json.dumps(event) + "\n")

    def handle_incident(self, module_path):
        self._audit({"action": "incident_start", "module": module_path})
        from inspector.static_inspector import StaticInspector
        inspector = StaticInspector()
        report = inspector.inspect(module_path)
        if report.get("severity", 0) < 5:
            self._audit({"action": "incident_skip", "reason": "low_severity"})
            return {"repaired": False, "reason": "Severity below threshold"}
        incident_id = self.incident_handler.log_incident({"module_path": module_path, "severity": report["severity"], "issues": report["issues"]})
        snapshot_id = self.incident_handler.create_snapshot(module_path)
        patch = self.repair_engine.generate_patch(report["issues"])
        if not patch["replacements"]:
            self._audit({"action": "no_patch", "incident": incident_id})
            return {"repaired": False, "reason": "No applicable repairs"}
        success = self.incident_handler.apply_patch(module_path, patch)
        if not success:
            self._audit({"action": "patch_failed", "incident": incident_id})
            return {"repaired": False, "reason": "Patch application failed"}
        from tester.autonomous_tester import AutonomousTester
        tester = AutonomousTester()
        test_result = tester.test_module(module_path)
        if not test_result.passed:
            self.incident_handler.rollback(module_path, snapshot_id)
            self._audit({"action": "rollback", "incident": incident_id})
            return {"repaired": False, "reason": "Post-repair test failed", "rolled_back": True}
        self._audit({"action": "repair_success", "incident": incident_id})
        return {"repaired": True, "incident_id": incident_id, "snapshot_id": snapshot_id, "patch": patch, "test_passed": True}

    def promote_module(self, src_path, dst_dir):
        try:
            src = Path(src_path)
            dst = Path(dst_dir) / src.name
            shutil.copy2(src, dst)
            self._audit({"action": "promote", "src": str(src), "dst": str(dst)})
            return True
        except Exception as e:
            logger.error(f"Promotion failed: {e}")
            return False

    def run_continuous(self, watch_dir, interval_s=60):
        from tester.autonomous_tester import AutonomousTester
        tester = AutonomousTester()
        watch = Path(watch_dir)
        while True:
            modules = list(watch.glob("**/*.py"))
            for mod in modules:
                result = tester.test_module(str(mod))
                if not result.passed:
                    self.handle_incident(str(mod))
            time.sleep(interval_s)
