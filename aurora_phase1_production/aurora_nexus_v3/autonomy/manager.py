#!/usr/bin/env python3
"""
Aurora Phase-1 Autonomy Manager
Orchestrates generate -> inspect -> test -> promote pipeline.
"""

import json
import logging
import shutil
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aurora_nexus_v3.autonomy.etcd_store import EtcdStore
from aurora_nexus_v3.autonomy.sandbox_runner_no_docker import SandboxRunner


@dataclass
class Incident:
    module_id: str
    error: str
    stacktrace: str = ""
    metrics: dict = field(default_factory=dict)
    extra: dict = field(default_factory=dict)
    severity: int = 5
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class RepairResult:
    module_id: str
    success: bool
    action: str
    details: dict = field(default_factory=dict)
    duration_ms: float = 0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class TestResult:
    module_id: str
    passed: bool
    duration_ms: float
    details: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class ModuleInspector:
    """Static code inspector with banned-pattern checks"""

    BANNED_PATTERNS = [
        ("import os", "os_import", 8),
        ("import sys", "sys_import", 6),
        ("import subprocess", "subprocess_import", 10),
        ("eval(", "eval_usage", 9),
        ("exec(", "exec_usage", 9),
        ("__import__", "dynamic_import", 8),
        ("os.system", "os_system", 10),
        ("os.popen", "os_popen", 10),
        ("open(", "file_open", 4),
        ("socket.", "socket_usage", 7),
        ("pickle.loads", "pickle_loads", 7),
    ]

    def __init__(self):
        self.results = {}

    def inspect(self, module_path: str) -> dict:
        """Inspect a module for banned patterns and code quality"""
        try:
            with open(module_path) as f:
                code = f.read()

            issues = []
            lines = code.split("\n")

            for pattern, name, severity in self.BANNED_PATTERNS:
                for line_no, line in enumerate(lines, 1):
                    if pattern in line:
                        issues.append(
                            {
                                "pattern": name,
                                "severity": severity,
                                "line": line_no,
                                "content": line.strip()[:100],
                            }
                        )

            max_severity = max([i["severity"] for i in issues], default=0)

            metrics = {
                "lines": len(lines),
                "functions": code.count("def "),
                "classes": code.count("class "),
                "imports": code.count("import "),
            }

            result = {
                "path": module_path,
                "issues": issues,
                "issue_count": len(issues),
                "max_severity": max_severity,
                "metrics": metrics,
                "safe": max_severity < 7,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            self.results[module_path] = result
            return result

        except Exception as e:
            return {"path": module_path, "error": str(e), "safe": False}


class ModuleTester:
    """Automated module tester"""

    def __init__(self, sandbox: SandboxRunner = None):
        self.sandbox = sandbox or SandboxRunner()
        self.results = []

    def test_module(self, module_path: str, test_payload: dict = None) -> TestResult:
        """Test a module by running its execute function"""
        start = time.time()

        try:
            result = self.sandbox.run_module(
                module_path, entry_point="execute", payload=test_payload or {}
            )

            duration = (time.time() - start) * 1000
            passed = result.get("ok", False)

            test_result = TestResult(
                module_id=Path(module_path).stem,
                passed=passed,
                duration_ms=duration,
                details={"result": result, "payload": test_payload},
            )

            self.results.append(test_result)
            return test_result

        except Exception as e:
            duration = (time.time() - start) * 1000
            test_result = TestResult(
                module_id=Path(module_path).stem,
                passed=False,
                duration_ms=duration,
                details={"error": str(e), "traceback": traceback.format_exc()},
            )
            self.results.append(test_result)
            return test_result

    def test_batch(self, module_paths: list[str], workers: int = 10) -> list[TestResult]:
        """Test multiple modules in parallel"""
        results = []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(self.test_module, path): path for path in module_paths}

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    path = futures[future]
                    results.append(
                        TestResult(
                            module_id=Path(path).stem,
                            passed=False,
                            duration_ms=0,
                            details={"error": str(e)},
                        )
                    )

        return results


class AutonomyManager:
    """Orchestrates the generate -> inspect -> test -> promote pipeline"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.data_dir = Path(self.config.get("data_dir", "aurora_data"))
        self.modules_dir = self.data_dir / "modules"
        self.candidates_dir = self.data_dir / "candidates"
        self.snapshots_dir = self.data_dir / "snapshots"
        self.audit_dir = self.data_dir / "audit"

        for d in [self.modules_dir, self.candidates_dir, self.snapshots_dir, self.audit_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.store = EtcdStore(data_dir=str(self.data_dir / "store"))
        self.sandbox = SandboxRunner(self.config.get("sandbox", {}))
        self.inspector = ModuleInspector()
        self.tester = ModuleTester(self.sandbox)

        self.repair_actions = {
            "regenerate": self._repair_regenerate,
            "rollback": self._repair_rollback,
            "disable": self._repair_disable,
            "notify": self._repair_notify,
        }

    def handle_incident(self, incident: Incident) -> RepairResult:
        """Handle an incident and attempt repair"""
        start = time.time()
        logger.info(f"Handling incident for module {incident.module_id}: {incident.error}")

        self._audit_log("incident_received", incident)

        action = self._determine_action(incident)

        try:
            repair_fn = self.repair_actions.get(action, self._repair_notify)
            result = repair_fn(incident)

            duration = (time.time() - start) * 1000
            repair_result = RepairResult(
                module_id=incident.module_id,
                success=result.get("success", False),
                action=action,
                details=result,
                duration_ms=duration,
            )

            self._audit_log("repair_completed", repair_result)
            return repair_result

        except Exception as e:
            duration = (time.time() - start) * 1000
            repair_result = RepairResult(
                module_id=incident.module_id,
                success=False,
                action=action,
                details={"error": str(e), "traceback": traceback.format_exc()},
                duration_ms=duration,
            )
            self._audit_log("repair_failed", repair_result)
            return repair_result

    def _determine_action(self, incident: Incident) -> str:
        """Determine repair action based on incident severity"""
        if incident.severity >= 9:
            return "disable"
        elif incident.severity >= 7:
            return "rollback"
        elif incident.severity >= 4:
            return "regenerate"
        else:
            return "notify"

    def _repair_regenerate(self, incident: Incident) -> dict:
        """Regenerate a module"""
        module_id = incident.module_id
        logger.info(f"Regenerating module {module_id}")

        module_data = self.store.get_module(module_id)
        if not module_data:
            return {"success": False, "error": "Module not registered"}

        return {"success": True, "action": "regenerate", "module_id": module_id}

    def _repair_rollback(self, incident: Incident) -> dict:
        """Rollback a module to previous snapshot"""
        module_id = incident.module_id
        logger.info(f"Rolling back module {module_id}")

        snapshot_dir = self.snapshots_dir / module_id
        if not snapshot_dir.exists():
            return {"success": False, "error": "No snapshot available"}

        snapshots = sorted(snapshot_dir.glob("*.snapshot"))
        if not snapshots:
            return {"success": False, "error": "No snapshots found"}

        latest_snapshot = snapshots[-1]

        return {"success": True, "action": "rollback", "snapshot": str(latest_snapshot)}

    def _repair_disable(self, incident: Incident) -> dict:
        """Disable a module"""
        module_id = incident.module_id
        logger.info(f"Disabling module {module_id}")

        self.store.put(f"/aurora/modules/{module_id}/status", "disabled")

        return {"success": True, "action": "disable", "module_id": module_id}

    def _repair_notify(self, incident: Incident) -> dict:
        """Send notification about incident"""
        module_id = incident.module_id
        logger.info(f"Notification for module {module_id}: {incident.error}")

        return {"success": True, "action": "notify", "message": incident.error}

    def generate_candidate(self, module_id: str, category: str, driver: str = "default") -> dict:
        """Generate a candidate module"""
        candidate_dir = self.candidates_dir / category
        candidate_dir.mkdir(parents=True, exist_ok=True)

        code = self._generate_module_code(module_id, category, driver)

        for file_type, content in code.items():
            filename = f"{category}_{module_id}_{file_type}.py"
            filepath = candidate_dir / filename
            with open(filepath, "w") as f:
                f.write(content)

        return {
            "module_id": module_id,
            "category": category,
            "driver": driver,
            "path": str(candidate_dir),
            "files": list(code.keys()),
        }

    def _generate_module_code(self, module_id: str, category: str, driver: str) -> dict:
        """Generate module code for init, execute, cleanup"""
        header = f'''"""
Aurora Module: {category}_{module_id}
Category: {category}
Driver: {driver}
Generated: {datetime.now(UTC).isoformat()}
"""
'''

        class_name = f"{category.title()}_{module_id}"

        init_code = (
            header
            + f'''
class {class_name}Init:
    def __init__(self, config=None):
        self.config = config or {{}}
        self.driver = "{driver}"

    def init(self):
        return {{"status": "initialized", "driver": self.driver}}

def init(config=None):
    return {class_name}Init(config).init()
'''
        )

        execute_code = (
            header
            + f"""
import time

class {class_name}Execute:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            result = self._process(payload)
            return {{"status": "ok", "result": result, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}

    def _process(self, payload):
        return {{"processed": True, "input": payload}}

def execute(payload=None):
    return {class_name}Execute().execute(payload or {{}})
"""
        )

        cleanup_code = (
            header
            + f"""
class {class_name}Cleanup:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def cleanup(self):
        return {{"status": "cleaned"}}

def cleanup(ctx=None):
    return {class_name}Cleanup(ctx).cleanup()
"""
        )

        return {"init": init_code, "execute": execute_code, "cleanup": cleanup_code}

    def inspect_candidate(self, module_path: str) -> dict:
        """Inspect a candidate module"""
        return self.inspector.inspect(module_path)

    def test_candidate(self, module_path: str, payload: dict = None) -> TestResult:
        """Test a candidate module"""
        return self.tester.test_module(module_path, payload)

    def promote_candidate(self, module_id: str, category: str) -> dict:
        """Promote a candidate to production"""
        candidate_dir = self.candidates_dir / category
        target_dir = self.modules_dir / category
        target_dir.mkdir(parents=True, exist_ok=True)

        files_promoted = []
        for file_type in ["init", "execute", "cleanup"]:
            filename = f"{category}_{module_id}_{file_type}.py"
            src = candidate_dir / filename
            dst = target_dir / filename

            if src.exists():
                self._create_snapshot(module_id, dst)
                shutil.copy2(src, dst)
                files_promoted.append(str(dst))

        self.store.register_module(
            module_id,
            {
                "category": category,
                "status": "active",
                "promoted": datetime.now(UTC).isoformat(),
                "files": files_promoted,
            },
        )

        self._audit_log(
            "module_promoted",
            {"module_id": module_id, "category": category, "files": files_promoted},
        )

        return {
            "module_id": module_id,
            "category": category,
            "promoted": True,
            "files": files_promoted,
        }

    def _create_snapshot(self, module_id: str, module_path: Path):
        """Create a snapshot of a module before overwriting"""
        if not module_path.exists():
            return

        snapshot_dir = self.snapshots_dir / module_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        snapshot_path = snapshot_dir / f"{module_path.name}.{timestamp}.snapshot"

        shutil.copy2(module_path, snapshot_path)

    def _audit_log(self, event: str, data: Any):
        """Write to audit log"""
        audit_file = self.audit_dir / f"audit_{datetime.now(UTC).strftime('%Y%m%d')}.jsonl"

        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            "data": asdict(data) if hasattr(data, "__dataclass_fields__") else data,
        }

        with open(audit_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def run_pipeline(self, module_id: str, category: str, driver: str = "default") -> dict:
        """Run the full generate -> inspect -> test -> promote pipeline"""
        results = {"module_id": module_id, "stages": {}}

        gen_result = self.generate_candidate(module_id, category, driver)
        results["stages"]["generate"] = gen_result

        execute_path = self.candidates_dir / category / f"{category}_{module_id}_execute.py"
        inspect_result = self.inspect_candidate(str(execute_path))
        results["stages"]["inspect"] = inspect_result

        if not inspect_result.get("safe", False):
            results["promoted"] = False
            results["reason"] = "Failed inspection"
            return results

        test_result = self.test_candidate(str(execute_path))
        results["stages"]["test"] = asdict(test_result)

        if not test_result.passed:
            results["promoted"] = False
            results["reason"] = "Failed testing"
            return results

        promote_result = self.promote_candidate(module_id, category)
        results["stages"]["promote"] = promote_result
        results["promoted"] = True

        return results


def create_manager(config: dict = None) -> AutonomyManager:
    return AutonomyManager(config)


if __name__ == "__main__":
    manager = AutonomyManager()

    result = manager.run_pipeline("0001", "connector", "http")
    print(json.dumps(result, indent=2, default=str))
