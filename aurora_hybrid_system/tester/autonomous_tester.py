import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class TestResult:
    def __init__(self, module_id, passed, duration_ms, details=None):
        self.module_id = module_id
        self.passed = passed
        self.duration_ms = duration_ms
        self.details = details or {}
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "module_id": self.module_id,
            "passed": self.passed,
            "duration_ms": self.duration_ms,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class AutonomousTester:
    def __init__(self, sandbox_mode="hybrid", max_workers=100):
        self.sandbox_mode = sandbox_mode
        self.max_workers = max_workers
        self.results = []

    def _get_sandbox(self):
        if self.sandbox_mode == "pure":
            from sandbox.sandbox_pure.pure_sandbox import PureSandbox

            return PureSandbox(cpu_limit_s=2, mem_limit_mb=64, timeout_s=5)
        else:
            from sandbox.sandbox_hybrid.hybrid_sandbox import HybridSandbox

            return HybridSandbox(cpu_limit_s=2, mem_limit_mb=64, timeout_s=5)

    def test_module(self, module_path, test_payload=None):
        start = time.time()
        sandbox = self._get_sandbox()
        try:
            result = sandbox.run_module(module_path, entry="execute", payload=test_payload or {})
            passed = result.get("ok", False)
            duration = (time.time() - start) * 1000
            return TestResult(
                module_id=str(module_path), passed=passed, duration_ms=duration, details=result
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            return TestResult(
                module_id=str(module_path),
                passed=False,
                duration_ms=duration,
                details={"error": str(e)},
            )

    def validate_output(self, result):
        issues = []
        if not isinstance(result, dict):
            issues.append("Output is not a dict")
            return {"valid": False, "issues": issues}
        if "ok" not in result and "status" not in result:
            issues.append("Missing ok/status field")
        if result.get("error") and result.get("ok", True):
            issues.append("Error present but ok=True")
        return {"valid": len(issues) == 0, "issues": issues}

    def detect_performance_anomaly(self, result, threshold_ms=1000):
        anomalies = []
        if result.duration_ms > threshold_ms:
            anomalies.append(f"Slow execution: {result.duration_ms:.1f}ms > {threshold_ms}ms")
        if result.details.get("timeout"):
            anomalies.append("Execution timed out")
        return {"anomalies": anomalies, "has_anomaly": len(anomalies) > 0}

    def test_batch(self, module_paths, test_payloads=None):
        results = []
        test_payloads = test_payloads or {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.test_module, path, test_payloads.get(path)): path
                for path in module_paths
            }
            for future in as_completed(futures):
                path = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(TestResult(path, False, 0, {"error": str(e)}))
        self.results.extend(results)
        return results

    def generate_report(self, results=None):
        results = results or self.results
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        avg_duration = sum(r.duration_ms for r in results) / total if total > 0 else 0
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "avg_duration_ms": avg_duration,
            "failures": [r.to_dict() for r in results if not r.passed],
        }

    def create_incident(self, result):
        return {
            "type": "module_test_failure",
            "module_id": result.module_id,
            "severity": 7 if result.details.get("timeout") else 5,
            "details": result.details,
            "timestamp": result.timestamp,
            "action": "repair",
        }
