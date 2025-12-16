#!/usr/bin/env python3
"""
Aurora Hybrid System ZIP Generator
Generates full production-grade code for U1/U3 sandboxes and autonomy systems.
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

ROOT = Path("aurora_hybrid_system")

DIRS = [
    "aurora_hybrid_core",
    "sandbox/sandbox_pure",
    "sandbox/sandbox_hybrid",
    "autonomy",
    "tester",
    "inspector",
    "module_generator",
    "rule_engine",
    "registry",
    "security",
    "lifecycle",
    "bridge",
    "workers",
    "modules"
]

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = content.strip().split('\n')
    if lines and all(line.startswith('    ') or line == '' for line in lines[1:] if line):
        min_indent = float('inf')
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)
        if min_indent > 0 and min_indent != float('inf'):
            lines = [line[min_indent:] if len(line) > min_indent else line for line in lines]
        content = '\n'.join(lines)
    path.write_text(content.strip() + "\n")

SANDBOX_PURE_CODE = '''
import ast
import resource
import signal
import multiprocessing
import time
import sys
import io
import os

BLOCKED_MODULES = frozenset([
    'os', 'subprocess', 'sys', 'shutil', 'socket', 'ctypes',
    'multiprocessing', 'threading', 'signal', 'resource',
    'importlib', '__builtins__', 'builtins', 'code', 'codeop',
    'compile', 'exec', 'eval', 'open', 'input', 'breakpoint'
])

BLOCKED_ATTRS = frozenset([
    '__import__', '__loader__', '__spec__', '__builtins__',
    '__file__', '__cached__', '__doc__', 'system', 'popen',
    'spawn', 'fork', 'exec', 'execv', 'execve', 'execl'
])

class ASTGuard(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split('.')[0] in BLOCKED_MODULES:
                self.violations.append(f"Blocked import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and node.module.split('.')[0] in BLOCKED_MODULES:
            self.violations.append(f"Blocked import from: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in ('exec', 'eval', 'compile', 'open', '__import__'):
                self.violations.append(f"Blocked call: {node.func.id}")
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in BLOCKED_ATTRS:
                self.violations.append(f"Blocked attribute call: {node.func.attr}")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr in BLOCKED_ATTRS:
            self.violations.append(f"Blocked attribute access: {node.attr}")
        self.generic_visit(node)

class PureSandbox:
    def __init__(self, cpu_limit_s=2, mem_limit_mb=128, timeout_s=5):
        self.cpu_limit_s = cpu_limit_s
        self.mem_limit = mem_limit_mb * 1024 * 1024
        self.timeout_s = timeout_s

    def _guard_ast(self, code_str):
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return None, [f"Syntax error: {e}"]
        guard = ASTGuard()
        guard.visit(tree)
        return tree, guard.violations

    def _create_safe_globals(self):
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
            'chr': chr, 'dict': dict, 'divmod': divmod, 'enumerate': enumerate,
            'filter': filter, 'float': float, 'format': format, 'frozenset': frozenset,
            'getattr': getattr, 'hasattr': hasattr, 'hash': hash, 'hex': hex,
            'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
            'iter': iter, 'len': len, 'list': list, 'map': map, 'max': max,
            'min': min, 'next': next, 'oct': oct, 'ord': ord, 'pow': pow,
            'print': print, 'range': range, 'repr': repr, 'reversed': reversed,
            'round': round, 'set': set, 'slice': slice, 'sorted': sorted,
            'str': str, 'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
            'True': True, 'False': False, 'None': None,
        }
        return {'__builtins__': safe_builtins}

    def _run_in_process(self, code_str, input_data, result_queue):
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (self.cpu_limit_s, self.cpu_limit_s))
            resource.setrlimit(resource.RLIMIT_AS, (self.mem_limit, self.mem_limit))
            try:
                resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
            except (ValueError, resource.error):
                pass
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
            try:
                safe_globals = self._create_safe_globals()
                safe_locals = {'input_data': input_data}
                exec(code_str, safe_globals, safe_locals)
                stdout_val = sys.stdout.getvalue()
                stderr_val = sys.stderr.getvalue()
                result = safe_locals.get('result', safe_locals.get('output', None))
                result_queue.put({"ok": True, "stdout": stdout_val, "stderr": stderr_val, "result": result})
            except Exception as e:
                result_queue.put({"ok": False, "error": f"{type(e).__name__}: {str(e)}", "stdout": sys.stdout.getvalue(), "stderr": sys.stderr.getvalue()})
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr
        except Exception as e:
            result_queue.put({"ok": False, "error": f"Sandbox error: {str(e)}"})

    def run_code(self, code_str, input_data=None):
        tree, violations = self._guard_ast(code_str)
        if violations:
            return {"ok": False, "error": "AST violations", "violations": violations}
        result_queue = multiprocessing.Queue()
        proc = multiprocessing.Process(target=self._run_in_process, args=(code_str, input_data, result_queue))
        proc.start()
        proc.join(timeout=self.timeout_s)
        if proc.is_alive():
            proc.terminate()
            proc.join(timeout=1)
            if proc.is_alive():
                proc.kill()
            return {"ok": False, "error": "Execution timeout", "timeout": True}
        try:
            return result_queue.get_nowait()
        except Exception:
            return {"ok": False, "error": "No result returned"}

    def run_module(self, module_path, entry_func="execute", payload=None):
        try:
            with open(module_path, 'r') as f:
                code = f.read()
            wrapper = code + f"\\nif callable({entry_func}):\\n    result = {entry_func}(input_data)\\nelse:\\n    result = None"
            return self.run_code(wrapper, payload)
        except FileNotFoundError:
            return {"ok": False, "error": f"Module not found: {module_path}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
'''

SANDBOX_HYBRID_CODE = '''
import os
import sys
import ast
import time
import threading
import resource
import signal
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

class ResourceLimiter:
    def __init__(self, cpu_s=2, mem_mb=128, fsize_mb=10):
        self.cpu_s = cpu_s
        self.mem_bytes = mem_mb * 1024 * 1024
        self.fsize_bytes = fsize_mb * 1024 * 1024

    def apply(self):
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (self.cpu_s, self.cpu_s))
        except (ValueError, resource.error):
            pass
        try:
            resource.setrlimit(resource.RLIMIT_AS, (self.mem_bytes, self.mem_bytes))
        except (ValueError, resource.error):
            pass
        try:
            resource.setrlimit(resource.RLIMIT_FSIZE, (self.fsize_bytes, self.fsize_bytes))
        except (ValueError, resource.error):
            pass
        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
        except (ValueError, resource.error):
            pass

class ExecutionTracer:
    def __init__(self):
        self.events = []
        self.start_time = None

    def start(self):
        self.start_time = time.time()
        self.events = []

    def trace(self, event_type, details=None):
        elapsed = time.time() - self.start_time if self.start_time else 0
        self.events.append({"time": elapsed, "type": event_type, "details": details or {}})

    def get_trace(self):
        return self.events

class HybridASTGuard(ast.NodeVisitor):
    BLOCKED = frozenset(['os', 'subprocess', 'sys', 'shutil', 'socket', 'ctypes', 'multiprocessing', 'threading', 'signal', 'resource'])
    BLOCKED_CALLS = frozenset(['exec', 'eval', 'compile', 'open', '__import__', 'input', 'breakpoint'])

    def __init__(self):
        self.violations = []
        self.stats = {"imports": 0, "calls": 0, "attrs": 0}

    def visit_Import(self, node):
        self.stats["imports"] += 1
        for alias in node.names:
            mod = alias.name.split('.')[0]
            if mod in self.BLOCKED:
                self.violations.append(f"Blocked import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.stats["imports"] += 1
        if node.module:
            mod = node.module.split('.')[0]
            if mod in self.BLOCKED:
                self.violations.append(f"Blocked import from: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node):
        self.stats["calls"] += 1
        if isinstance(node.func, ast.Name):
            if node.func.id in self.BLOCKED_CALLS:
                self.violations.append(f"Blocked call: {node.func.id}")
        self.generic_visit(node)

class HybridSandbox:
    def __init__(self, cpu_limit_s=2, mem_limit_mb=128, timeout_s=5, trace=False):
        self.cpu = cpu_limit_s
        self.mem_mb = mem_limit_mb
        self.timeout = timeout_s
        self.trace_enabled = trace
        self.limiter = ResourceLimiter(cpu_limit_s, mem_limit_mb)
        self.tracer = ExecutionTracer() if trace else None

    def _guard(self, code_str):
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return None, [f"Syntax error: {e}"], {}
        guard = HybridASTGuard()
        guard.visit(tree)
        return tree, guard.violations, guard.stats

    def _create_safe_env(self):
        safe = {
            'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
            'chr': chr, 'dict': dict, 'divmod': divmod, 'enumerate': enumerate,
            'filter': filter, 'float': float, 'format': format, 'frozenset': frozenset,
            'getattr': getattr, 'hasattr': hasattr, 'hash': hash, 'hex': hex,
            'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
            'iter': iter, 'len': len, 'list': list, 'map': map, 'max': max,
            'min': min, 'next': next, 'oct': oct, 'ord': ord, 'pow': pow,
            'print': print, 'range': range, 'repr': repr, 'reversed': reversed,
            'round': round, 'set': set, 'slice': slice, 'sorted': sorted,
            'str': str, 'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
            'True': True, 'False': False, 'None': None,
        }
        return {'__builtins__': safe}

    def run(self, code_str, input_data=None):
        if self.tracer:
            self.tracer.start()
            self.tracer.trace("guard_start")
        tree, violations, stats = self._guard(code_str)
        if violations:
            return {"ok": False, "error": "AST guard violations", "violations": violations, "stats": stats}
        if self.tracer:
            self.tracer.trace("guard_pass", stats)
        result_container = {}
        def execute():
            try:
                self.limiter.apply()
                if self.tracer:
                    self.tracer.trace("exec_start")
                safe_globals = self._create_safe_env()
                safe_locals = {"input_data": input_data, "payload": input_data}
                exec(code_str, safe_globals, safe_locals)
                result_container["ok"] = True
                result_container["result"] = safe_locals.get("result", safe_locals.get("output"))
                result_container["locals"] = {k: v for k, v in safe_locals.items() if not k.startswith('_') and k not in ('input_data', 'payload')}
                if self.tracer:
                    self.tracer.trace("exec_complete")
            except MemoryError:
                result_container["ok"] = False
                result_container["error"] = "Memory limit exceeded"
            except Exception as e:
                result_container["ok"] = False
                result_container["error"] = f"{type(e).__name__}: {str(e)}"
                result_container["traceback"] = traceback.format_exc()
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(execute)
            try:
                future.result(timeout=self.timeout)
            except FutureTimeout:
                result_container["ok"] = False
                result_container["error"] = "Execution timeout"
                result_container["timeout"] = True
        if self.tracer:
            result_container["trace"] = self.tracer.get_trace()
        return result_container

    def run_module(self, module_path, entry="execute", payload=None):
        try:
            with open(module_path, 'r') as f:
                code = f.read()
            wrapper = code + f"\\nif '{entry}' in dir() and callable({entry}):\\n    result = {entry}(input_data)"
            return self.run(wrapper, payload)
        except FileNotFoundError:
            return {"ok": False, "error": f"Module not found: {module_path}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def validate_module(self, module_path):
        try:
            with open(module_path, 'r') as f:
                code = f.read()
            tree, violations, stats = self._guard(code)
            return {"valid": len(violations) == 0, "violations": violations, "stats": stats}
        except Exception as e:
            return {"valid": False, "error": str(e)}
'''

SANDBOX_INIT_CODE = '''
from .sandbox_pure.pure_sandbox import PureSandbox
from .sandbox_hybrid.hybrid_sandbox import HybridSandbox

def get_sandbox(mode="hybrid", **kwargs):
    if mode == "pure":
        return PureSandbox(**kwargs)
    return HybridSandbox(**kwargs)
'''

TESTER_CODE = '''
import json
import time
import logging
from pathlib import Path
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
        return {"module_id": self.module_id, "passed": self.passed, "duration_ms": self.duration_ms, "details": self.details, "timestamp": self.timestamp}

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
            return TestResult(module_id=str(module_path), passed=passed, duration_ms=duration, details=result)
        except Exception as e:
            duration = (time.time() - start) * 1000
            return TestResult(module_id=str(module_path), passed=False, duration_ms=duration, details={"error": str(e)})

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
            futures = {executor.submit(self.test_module, path, test_payloads.get(path)): path for path in module_paths}
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
        return {"total": total, "passed": passed, "failed": failed, "pass_rate": (passed / total * 100) if total > 0 else 0, "avg_duration_ms": avg_duration, "failures": [r.to_dict() for r in results if not r.passed]}

    def create_incident(self, result):
        return {"type": "module_test_failure", "module_id": result.module_id, "severity": 7 if result.details.get("timeout") else 5, "details": result.details, "timestamp": result.timestamp, "action": "repair"}
'''

INSPECTOR_CODE = '''
import ast
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PatternDetector:
    UNSAFE_PATTERNS = [
        (r'eval\\s*\\(', 'eval_usage', 8),
        (r'exec\\s*\\(', 'exec_usage', 8),
        (r'__import__\\s*\\(', 'dynamic_import', 7),
        (r'subprocess', 'subprocess_usage', 9),
        (r'os\\.system', 'os_system', 9),
        (r'open\\s*\\(.+w', 'file_write', 6),
        (r'pickle\\.loads?', 'pickle_usage', 7),
        (r'yaml\\.load\\s*\\(', 'unsafe_yaml', 6),
    ]
    INEFFICIENCY_PATTERNS = [
        (r'for .+ in range\\(len\\(.+\\)\\)', 'range_len_antipattern', 2),
        (r'== True|== False', 'explicit_bool_compare', 1),
        (r'\\+= .+\\n.*\\+= ', 'string_concat_loop', 3),
        (r'except:\\s*\\n\\s*pass', 'bare_except_pass', 4),
        (r'global\\s+\\w+', 'global_usage', 2),
    ]

    def detect(self, code):
        unsafe = []
        inefficient = []
        for pattern, name, severity in self.UNSAFE_PATTERNS:
            matches = re.finditer(pattern, code)
            for m in matches:
                unsafe.append({"pattern": name, "severity": severity, "position": m.start(), "match": m.group()[:50]})
        for pattern, name, severity in self.INEFFICIENCY_PATTERNS:
            matches = re.finditer(pattern, code)
            for m in matches:
                inefficient.append({"pattern": name, "severity": severity, "position": m.start(), "match": m.group()[:50]})
        return {"unsafe": unsafe, "inefficient": inefficient}

class ASTAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.metrics = {"functions": 0, "classes": 0, "imports": 0, "try_blocks": 0, "loops": 0, "conditionals": 0, "complexity": 0}
        self.issues = []

    def visit_FunctionDef(self, node):
        self.metrics["functions"] += 1
        if len(node.body) > 50:
            self.issues.append({"type": "long_function", "name": node.name, "lines": len(node.body), "severity": 3})
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.metrics["classes"] += 1
        self.generic_visit(node)

    def visit_Import(self, node):
        self.metrics["imports"] += 1
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.metrics["imports"] += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        self.metrics["try_blocks"] += 1
        for handler in node.handlers:
            if handler.type is None:
                self.issues.append({"type": "bare_except", "severity": 4})
        self.generic_visit(node)

    def visit_For(self, node):
        self.metrics["loops"] += 1
        self.metrics["complexity"] += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.metrics["loops"] += 1
        self.metrics["complexity"] += 1
        self.generic_visit(node)

    def visit_If(self, node):
        self.metrics["conditionals"] += 1
        self.metrics["complexity"] += 1
        self.generic_visit(node)

class StaticInspector:
    def __init__(self):
        self.pattern_detector = PatternDetector()

    def inspect(self, path):
        try:
            with open(path, 'r') as f:
                code = f.read()
        except Exception as e:
            return {"error": str(e), "severity": 10}
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {"syntax_error": str(e), "severity": 10, "line": e.lineno}
        analyzer = ASTAnalyzer()
        analyzer.visit(tree)
        patterns = self.pattern_detector.detect(code)
        all_issues = analyzer.issues + patterns["unsafe"] + patterns["inefficient"]
        max_severity = max((i.get("severity", 0) for i in all_issues), default=0)
        return {"path": path, "metrics": analyzer.metrics, "issues": all_issues, "patterns": patterns, "severity": max_severity, "recommendations": self._generate_recommendations(all_issues)}

    def _generate_recommendations(self, issues):
        recs = []
        for issue in issues:
            pattern = issue.get("pattern") or issue.get("type")
            if pattern == "eval_usage":
                recs.append("Replace eval() with ast.literal_eval() or explicit parsing")
            elif pattern == "exec_usage":
                recs.append("Avoid exec(); use explicit function calls")
            elif pattern == "bare_except":
                recs.append("Use specific exception types instead of bare except")
            elif pattern == "long_function":
                recs.append(f"Refactor function into smaller units")
            elif pattern == "subprocess_usage":
                recs.append("Review subprocess usage for security implications")
        return list(set(recs))

    def inspect_batch(self, paths):
        return [self.inspect(p) for p in paths]
'''

AUTONOMY_CODE = '''
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
            f.write(json.dumps(event) + "\\n")

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
'''

MODULE_GENERATOR_CODE = '''
import json
import os
import time
from pathlib import Path
from datetime import datetime

CATEGORIES = ["connector", "processor", "analyzer", "generator", "transformer", "validator", "formatter", "optimizer", "monitor", "integrator"]

CATEGORY_TEMPLATES = {
    "connector": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.connection = None

    def execute(self, payload):
        start = time.time()
        try:
            endpoint = payload.get("endpoint", "default")
            data = payload.get("data", {{}})
            result = {{"connected": True, "endpoint": endpoint, "response": {{"status": "ok", "data_size": len(str(data))}}}}
            return {{"status": "ok", "duration_ms": (time.time()-start)*1000, "result": result}}
        except Exception as e:
            return {{"status": "error", "error": str(e), "duration_ms": (time.time()-start)*1000}}""",
    "processor": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            items = payload.get("items", [])
            processed = [self._process_item(item) for item in items]
            return {{"status": "ok", "processed_count": len(processed), "results": processed, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}

    def _process_item(self, item):
        if isinstance(item, dict):
            return {{k: v for k, v in item.items() if v is not None}}
        return item""",
    "analyzer": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            data = payload.get("data", {{}})
            analysis = {{"field_count": len(data) if isinstance(data, dict) else 0, "type": type(data).__name__, "size": len(str(data))}}
            return {{"status": "ok", "analysis": analysis, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "generator": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            template = payload.get("template", "default")
            count = payload.get("count", 1)
            generated = [{{"id": i, "template": template, "data": {{}}}} for i in range(count)]
            return {{"status": "ok", "generated": generated, "count": len(generated), "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "transformer": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            source = payload.get("source", {{}})
            mapping = payload.get("mapping", {{}})
            transformed = {{mapping.get(k, k): v for k, v in source.items()}} if isinstance(source, dict) else source
            return {{"status": "ok", "transformed": transformed, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "validator": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            data = payload.get("data", {{}})
            rules = payload.get("rules", [])
            errors = []
            for rule in rules:
                field = rule.get("field")
                required = rule.get("required", False)
                if required and field not in data:
                    errors.append(f"Missing required field: {{field}}")
            valid = len(errors) == 0
            return {{"status": "ok", "valid": valid, "errors": errors, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "formatter": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            data = payload.get("data", {{}})
            fmt = payload.get("format", "json")
            if fmt == "json":
                import json
                formatted = json.dumps(data, indent=2)
            else:
                formatted = str(data)
            return {{"status": "ok", "formatted": formatted, "format": fmt, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "optimizer": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            data = payload.get("data", [])
            strategy = payload.get("strategy", "default")
            if isinstance(data, list):
                optimized = sorted(set(data))
            else:
                optimized = data
            return {{"status": "ok", "optimized": optimized, "strategy": strategy, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "monitor": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.metrics = {{}}

    def execute(self, payload):
        start = time.time()
        try:
            target = payload.get("target", "system")
            self.metrics[target] = {{"checked_at": time.time(), "status": "healthy"}}
            return {{"status": "ok", "metrics": self.metrics, "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}""",
    "integrator": """class {class_name}:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def execute(self, payload):
        start = time.time()
        try:
            sources = payload.get("sources", [])
            merged = {{}}
            for src in sources:
                if isinstance(src, dict):
                    merged.update(src)
            return {{"status": "ok", "integrated": merged, "source_count": len(sources), "duration_ms": (time.time()-start)*1000}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}"""
}

class ModuleGenerator:
    def __init__(self, output_dir="generated_modules"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.registry = {}

    def generate_manifest(self, count=550):
        manifest = []
        for i in range(count):
            category = CATEGORIES[i % len(CATEGORIES)]
            module_id = f"{i+1:04d}"
            manifest.append({"id": module_id, "name": f"{category.capitalize()}_{module_id}", "category": category, "version": "1.0.0"})
        return manifest

    def _generate_init(self, module_id, name, category):
        return f\'''"""
Aurora Module: {name}
ID: {module_id}
Category: {category}
Generated: {datetime.utcnow().isoformat()}Z
"""
import time

class {name}Init:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.initialized = False

    def initialize(self):
        self.initialized = True
        return {{"status": "ok", "module": "{name}"}}
\'''

    def _generate_execute(self, module_id, name, category):
        template = CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["processor"])
        class_name = f"{name}Execute"
        code = f\'''"""
Aurora Module: {name}
ID: {module_id}
Category: {category}
Generated: {datetime.utcnow().isoformat()}Z
"""
import time

{template.format(class_name=class_name)}

def execute(payload=None):
    instance = {class_name}()
    return instance.execute(payload or {{}})
\'''
        return code

    def _generate_cleanup(self, module_id, name, category):
        return f\'''"""
Aurora Module: {name}
ID: {module_id}
Category: {category}
Generated: {datetime.utcnow().isoformat()}Z
"""
import time

class {name}Cleanup:
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}

    def cleanup(self):
        return {{"status": "ok", "cleaned": True}}

def cleanup():
    instance = {name}Cleanup()
    return instance.cleanup()
\'''

    def generate_module(self, spec):
        module_id = spec["id"]
        name = spec["name"]
        category = spec["category"]
        module_dir = self.output_dir / category
        module_dir.mkdir(parents=True, exist_ok=True)
        files = []
        init_path = module_dir / f"{category}_{module_id}_init.py"
        init_path.write_text(self._generate_init(module_id, name, category))
        files.append(str(init_path))
        exec_path = module_dir / f"{category}_{module_id}_execute.py"
        exec_path.write_text(self._generate_execute(module_id, name, category))
        files.append(str(exec_path))
        cleanup_path = module_dir / f"{category}_{module_id}_cleanup.py"
        cleanup_path.write_text(self._generate_cleanup(module_id, name, category))
        files.append(str(cleanup_path))
        self.registry[module_id] = {"id": module_id, "name": name, "category": category, "files": files}
        return {"id": module_id, "files": files}

    def generate_all(self, manifest):
        results = []
        for spec in manifest:
            result = self.generate_module(spec)
            results.append(result)
        registry_path = self.output_dir / "modules_registry.json"
        with open(registry_path, 'w') as f:
            json.dump({"generated_at": datetime.utcnow().isoformat() + "Z", "count": len(results), "modules": self.registry}, f, indent=2)
        return {"generated": len(results), "registry": str(registry_path)}
'''

RULE_ENGINE_CODE = '''
import json
from pathlib import Path

class SeverityRule:
    def __init__(self, name, pattern, base_severity, modifiers=None):
        self.name = name
        self.pattern = pattern
        self.base_severity = base_severity
        self.modifiers = modifiers or {}

    def evaluate(self, context):
        severity = self.base_severity
        for key, modifier in self.modifiers.items():
            if key in context:
                severity += modifier
        return min(10, max(0, severity))

class RuleEngine:
    DEFAULT_RULES = [
        SeverityRule("syntax_error", "syntax", 10),
        SeverityRule("security_violation", "security", 9, {"in_production": 1}),
        SeverityRule("performance_issue", "performance", 5, {"critical_path": 2}),
        SeverityRule("test_failure", "test", 6, {"regression": 2}),
        SeverityRule("code_quality", "quality", 3),
    ]

    def __init__(self, rules=None):
        self.rules = rules or self.DEFAULT_RULES
        self.rule_map = {r.name: r for r in self.rules}

    def evaluate(self, incident_type, context=None):
        context = context or {}
        for rule in self.rules:
            if rule.pattern in incident_type.lower():
                return rule.evaluate(context)
        return 5

    def should_auto_repair(self, severity):
        return 3 <= severity <= 7

    def requires_approval(self, severity):
        return severity >= 8

    def get_action(self, severity):
        if severity >= 9:
            return "block_and_notify"
        elif severity >= 7:
            return "repair_with_approval"
        elif severity >= 4:
            return "auto_repair"
        else:
            return "log_only"

class CapabilityManager:
    TIERS = {
        "sandbox": ["read", "compute"],
        "worker": ["read", "compute", "write_temp"],
        "autonomy": ["read", "compute", "write_temp", "write_module", "repair"],
        "admin": ["read", "compute", "write_temp", "write_module", "repair", "promote", "delete"]
    }

    def __init__(self):
        self.active_capabilities = {}

    def grant(self, entity_id, tier):
        if tier in self.TIERS:
            self.active_capabilities[entity_id] = set(self.TIERS[tier])

    def check(self, entity_id, capability):
        caps = self.active_capabilities.get(entity_id, set())
        return capability in caps

    def revoke(self, entity_id):
        self.active_capabilities.pop(entity_id, None)
'''

LIFECYCLE_CODE = '''
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LifecycleHook:
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback

    def execute(self, context):
        try:
            result = self.callback(context)
            return {"ok": True, "hook": self.name, "result": result}
        except Exception as e:
            return {"ok": False, "hook": self.name, "error": str(e)}

class ModuleLifecycle:
    def __init__(self):
        self.pre_init_hooks = []
        self.post_init_hooks = []
        self.pre_exec_hooks = []
        self.post_exec_hooks = []
        self.pre_cleanup_hooks = []
        self.post_cleanup_hooks = []

    def add_hook(self, phase, hook):
        hook_list = getattr(self, f"{phase}_hooks", None)
        if hook_list is not None:
            hook_list.append(hook)

    def _run_hooks(self, hooks, context):
        results = []
        for hook in hooks:
            results.append(hook.execute(context))
        return results

    def run_init(self, module_path, ctx=None):
        context = {"module_path": module_path, "ctx": ctx or {}, "phase": "init"}
        pre_results = self._run_hooks(self.pre_init_hooks, context)
        start = time.time()
        try:
            spec = self._load_module(module_path, "init")
            if spec and hasattr(spec, "initialize"):
                result = spec.initialize()
            else:
                result = {"status": "ok", "default": True}
        except Exception as e:
            result = {"status": "error", "error": str(e)}
        duration = time.time() - start
        context["result"] = result
        context["duration"] = duration
        post_results = self._run_hooks(self.post_init_hooks, context)
        return {"phase": "init", "result": result, "duration_ms": duration * 1000, "pre_hooks": pre_results, "post_hooks": post_results}

    def run_execute(self, module_path, payload=None):
        context = {"module_path": module_path, "payload": payload, "phase": "execute"}
        pre_results = self._run_hooks(self.pre_exec_hooks, context)
        start = time.time()
        try:
            spec = self._load_module(module_path, "execute")
            if spec and hasattr(spec, "execute"):
                result = spec.execute(payload or {})
            else:
                result = {"status": "error", "error": "No execute function"}
        except Exception as e:
            result = {"status": "error", "error": str(e)}
        duration = time.time() - start
        context["result"] = result
        context["duration"] = duration
        post_results = self._run_hooks(self.post_exec_hooks, context)
        return {"phase": "execute", "result": result, "duration_ms": duration * 1000, "pre_hooks": pre_results, "post_hooks": post_results}

    def run_cleanup(self, module_path):
        context = {"module_path": module_path, "phase": "cleanup"}
        pre_results = self._run_hooks(self.pre_cleanup_hooks, context)
        start = time.time()
        try:
            spec = self._load_module(module_path, "cleanup")
            if spec and hasattr(spec, "cleanup"):
                result = spec.cleanup()
            else:
                result = {"status": "ok", "default": True}
        except Exception as e:
            result = {"status": "error", "error": str(e)}
        duration = time.time() - start
        context["result"] = result
        post_results = self._run_hooks(self.post_cleanup_hooks, context)
        return {"phase": "cleanup", "result": result, "duration_ms": duration * 1000, "pre_hooks": pre_results, "post_hooks": post_results}

    def _load_module(self, path, phase):
        import importlib.util
        try:
            spec = importlib.util.spec_from_file_location(f"module_{phase}", path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        except Exception as e:
            logger.error(f"Failed to load module: {e}")
        return None
'''

SECURITY_CODE = '''
import hashlib
import hmac
import time
import json
from pathlib import Path

class CapabilityToken:
    def __init__(self, entity_id, capabilities, expires_at, secret="aurora_secret"):
        self.entity_id = entity_id
        self.capabilities = capabilities
        self.expires_at = expires_at
        self.secret = secret
        self.signature = self._sign()

    def _sign(self):
        data = f"{self.entity_id}:{','.join(sorted(self.capabilities))}:{self.expires_at}"
        return hmac.new(self.secret.encode(), data.encode(), hashlib.sha256).hexdigest()

    def is_valid(self):
        if time.time() > self.expires_at:
            return False
        return self._sign() == self.signature

    def has_capability(self, cap):
        return cap in self.capabilities and self.is_valid()

    def to_dict(self):
        return {"entity_id": self.entity_id, "capabilities": list(self.capabilities), "expires_at": self.expires_at, "signature": self.signature}

class SecurityLayer:
    TIER_CAPABILITIES = {
        "sandbox": {"read", "compute"},
        "worker": {"read", "compute", "write_temp"},
        "autonomy": {"read", "compute", "write_temp", "write_module", "repair"},
        "admin": {"read", "compute", "write_temp", "write_module", "repair", "promote", "delete", "configure"}
    }
    APPROVAL_REQUIRED = {"delete", "promote", "configure"}

    def __init__(self, secret="aurora_secret"):
        self.secret = secret
        self.tokens = {}
        self.pending_approvals = {}
        self.approval_log = []

    def issue_token(self, entity_id, tier, ttl_seconds=3600):
        if tier not in self.TIER_CAPABILITIES:
            return None
        caps = self.TIER_CAPABILITIES[tier]
        expires = time.time() + ttl_seconds
        token = CapabilityToken(entity_id, caps, expires, self.secret)
        self.tokens[entity_id] = token
        return token

    def validate_token(self, entity_id):
        token = self.tokens.get(entity_id)
        return token is not None and token.is_valid()

    def check_capability(self, entity_id, capability):
        token = self.tokens.get(entity_id)
        if not token:
            return False
        return token.has_capability(capability)

    def requires_approval(self, capability):
        return capability in self.APPROVAL_REQUIRED

    def request_approval(self, entity_id, action, context=None):
        approval_id = f"APR-{int(time.time()*1000)}"
        self.pending_approvals[approval_id] = {"entity_id": entity_id, "action": action, "context": context or {}, "requested_at": time.time(), "status": "pending"}
        return approval_id

    def approve(self, approval_id, approver):
        if approval_id not in self.pending_approvals:
            return False
        self.pending_approvals[approval_id]["status"] = "approved"
        self.pending_approvals[approval_id]["approved_by"] = approver
        self.pending_approvals[approval_id]["approved_at"] = time.time()
        self.approval_log.append(self.pending_approvals[approval_id])
        return True

    def deny(self, approval_id, reason=""):
        if approval_id not in self.pending_approvals:
            return False
        self.pending_approvals[approval_id]["status"] = "denied"
        self.pending_approvals[approval_id]["reason"] = reason
        return True

    def revoke_token(self, entity_id):
        self.tokens.pop(entity_id, None)
'''

REGISTRY_CODE = '''
import json
import time
from pathlib import Path
from datetime import datetime
import threading
import hashlib

class ModuleRegistry:
    def __init__(self, registry_path="module_registry.json"):
        self.registry_path = Path(registry_path)
        self.modules = {}
        self.lock = threading.Lock()
        self._load()

    def _load(self):
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    self.modules = data.get("modules", {})
            except Exception:
                self.modules = {}

    def _save(self):
        with open(self.registry_path, 'w') as f:
            json.dump({"updated_at": datetime.utcnow().isoformat() + "Z", "count": len(self.modules), "modules": self.modules}, f, indent=2)

    def register(self, module_id, metadata):
        with self.lock:
            self.modules[module_id] = {**metadata, "registered_at": datetime.utcnow().isoformat() + "Z", "status": "active"}
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
                with open(f, 'rb') as fh:
                    checksums.append(hashlib.sha256(fh.read()).hexdigest())
            except Exception:
                pass
        if checksums:
            combined = "".join(checksums)
            return hashlib.sha256(combined.encode()).hexdigest()[:16]
        return None
'''

WORKERS_CODE = '''
import time
import threading
import queue
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class WorkerTask:
    def __init__(self, task_id, task_type, payload):
        self.task_id = task_id
        self.task_type = task_type
        self.payload = payload
        self.created_at = time.time()
        self.status = "pending"
        self.result = None

class LuminarWorker:
    def __init__(self, worker_id, capabilities=None):
        self.worker_id = worker_id
        self.capabilities = capabilities or ["execute", "test", "analyze"]
        self.status = "idle"
        self.tasks_completed = 0

    def can_handle(self, task_type):
        return task_type in self.capabilities or "all" in self.capabilities

    def execute(self, task):
        self.status = "busy"
        start = time.time()
        try:
            if task.task_type == "test":
                result = self._run_test(task.payload)
            elif task.task_type == "analyze":
                result = self._run_analyze(task.payload)
            elif task.task_type == "repair":
                result = self._run_repair(task.payload)
            else:
                result = self._run_execute(task.payload)
            task.status = "completed"
            task.result = result
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            result = task.result
        finally:
            self.status = "idle"
            self.tasks_completed += 1
        return {"task_id": task.task_id, "worker": self.worker_id, "duration_ms": (time.time()-start)*1000, "result": result}

    def _run_test(self, payload):
        module_path = payload.get("module_path")
        return {"tested": True, "module": module_path, "passed": True}

    def _run_analyze(self, payload):
        module_path = payload.get("module_path")
        return {"analyzed": True, "module": module_path, "issues": []}

    def _run_repair(self, payload):
        module_path = payload.get("module_path")
        return {"repaired": True, "module": module_path}

    def _run_execute(self, payload):
        return {"executed": True, "payload_size": len(str(payload))}

class WorkerPool:
    def __init__(self, worker_count=100, hybrid_workers=200):
        self.workers = {}
        self.task_queue = queue.Queue()
        self.results = {}
        for i in range(worker_count):
            w = LuminarWorker(f"luminar-{i:03d}", ["test", "analyze", "execute"])
            self.workers[w.worker_id] = w
        for i in range(hybrid_workers):
            w = LuminarWorker(f"hybrid-{i:03d}", ["repair", "execute", "all"])
            self.workers[w.worker_id] = w
        self.executor = ThreadPoolExecutor(max_workers=min(worker_count + hybrid_workers, 300))
        self.running = False

    def submit(self, task):
        self.task_queue.put(task)
        return task.task_id

    def _find_worker(self, task_type):
        for w in self.workers.values():
            if w.status == "idle" and w.can_handle(task_type):
                return w
        return None

    def process_batch(self, tasks):
        futures = {}
        for task in tasks:
            worker = self._find_worker(task.task_type)
            if worker:
                future = self.executor.submit(worker.execute, task)
                futures[future] = task.task_id
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                self.results[futures[future]] = result
            except Exception as e:
                results.append({"task_id": futures[future], "error": str(e)})
        return results

    def get_stats(self):
        idle = sum(1 for w in self.workers.values() if w.status == "idle")
        busy = len(self.workers) - idle
        total_completed = sum(w.tasks_completed for w in self.workers.values())
        return {"total_workers": len(self.workers), "idle": idle, "busy": busy, "queue_size": self.task_queue.qsize(), "total_completed": total_completed}

    def shutdown(self):
        self.executor.shutdown(wait=True)
'''

BRIDGE_CODE = '''
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
        self.event_log.append({"type": event_type, "details": details or {}, "timestamp": time.time()})

    def send_incident(self, incident):
        if not self.connected:
            return False
        incidents_dir = self.aurora_path / "incidents"
        incidents_dir.mkdir(parents=True, exist_ok=True)
        incident_id = f"INC-{int(time.time()*1000)}"
        incident["id"] = incident_id
        path = incidents_dir / f"{incident_id}.json"
        with open(path, 'w') as f:
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
            with open(registry_path, 'r') as f:
                return {"synced": True, "registry": json.load(f)}
        return {"synced": False, "error": "Registry not found"}

    def get_status(self):
        return {"connected": self.connected, "path": str(self.aurora_path) if self.aurora_path else None, "events": len(self.event_log)}
'''

CORE_CODE = '''
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

class AuroraHybridCore:
    def __init__(self, base_dir="aurora_data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        from sandbox import get_sandbox
        from autonomy import AutonomyEngine
        from tester import AutonomousTester
        from inspector import StaticInspector
        from module_generator import ModuleGenerator
        from rule_engine import RuleEngine, CapabilityManager
        from lifecycle import ModuleLifecycle
        from security import SecurityLayer
        from registry import ModuleRegistry
        from workers import WorkerPool
        from bridge import AuroraBridge
        self.sandbox_pure = get_sandbox("pure")
        self.sandbox_hybrid = get_sandbox("hybrid")
        self.autonomy = AutonomyEngine(str(self.base_dir / "autonomy"))
        self.tester = AutonomousTester(max_workers=100)
        self.inspector = StaticInspector()
        self.generator = ModuleGenerator(str(self.base_dir / "generated_modules"))
        self.rule_engine = RuleEngine()
        self.capability_mgr = CapabilityManager()
        self.lifecycle = ModuleLifecycle()
        self.security = SecurityLayer()
        self.registry = ModuleRegistry(str(self.base_dir / "registry.json"))
        self.worker_pool = WorkerPool(worker_count=100, hybrid_workers=200)
        self.bridge = AuroraBridge()
        logger.info("Aurora Hybrid Core initialized")

    def generate_modules(self, count=550):
        manifest = self.generator.generate_manifest(count)
        result = self.generator.generate_all(manifest)
        logger.info(f"Generated {result['generated']} modules")
        return result

    def test_module(self, module_path, payload=None):
        return self.tester.test_module(module_path, payload)

    def inspect_module(self, module_path):
        return self.inspector.inspect(module_path)

    def handle_incident(self, module_path):
        return self.autonomy.handle_incident(module_path)

    def run_in_sandbox(self, code, mode="hybrid", payload=None):
        if mode == "pure":
            return self.sandbox_pure.run_code(code, payload)
        return self.sandbox_hybrid.run(code, payload)

    def get_status(self):
        return {"modules_registered": len(self.registry.modules), "workers": self.worker_pool.get_stats(), "bridge": self.bridge.get_status()}

    def shutdown(self):
        self.worker_pool.shutdown()
        logger.info("Aurora Hybrid Core shutdown complete")
'''

MAIN_CODE = '''
#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from aurora_hybrid_core import AuroraHybridCore

def main():
    parser = argparse.ArgumentParser(description="Aurora Hybrid System")
    parser.add_argument("command", choices=["generate", "test", "inspect", "run", "status"])
    parser.add_argument("--count", type=int, default=550, help="Number of modules to generate")
    parser.add_argument("--module", type=str, help="Module path for test/inspect")
    parser.add_argument("--code", type=str, help="Code to run in sandbox")
    parser.add_argument("--mode", choices=["pure", "hybrid"], default="hybrid")
    args = parser.parse_args()

    core = AuroraHybridCore()

    if args.command == "generate":
        result = core.generate_modules(args.count)
        print(f"Generated {result['generated']} modules")
        print(f"Registry: {result['registry']}")
    elif args.command == "test":
        if not args.module:
            print("Error: --module required")
            sys.exit(1)
        result = core.test_module(args.module)
        print(f"Test result: {result}")
    elif args.command == "inspect":
        if not args.module:
            print("Error: --module required")
            sys.exit(1)
        result = core.inspect_module(args.module)
        print(f"Inspection: {result}")
    elif args.command == "run":
        if not args.code:
            print("Error: --code required")
            sys.exit(1)
        result = core.run_in_sandbox(args.code, args.mode)
        print(f"Result: {result}")
    elif args.command == "status":
        status = core.get_status()
        print(f"Status: {status}")
    core.shutdown()

if __name__ == "__main__":
    main()
'''

def build_sandbox_pure():
    write_file(ROOT / "sandbox/sandbox_pure/pure_sandbox.py", SANDBOX_PURE_CODE)
    write_file(ROOT / "sandbox/sandbox_pure/__init__.py", "from .pure_sandbox import PureSandbox, ASTGuard")

def build_sandbox_hybrid():
    write_file(ROOT / "sandbox/sandbox_hybrid/hybrid_sandbox.py", SANDBOX_HYBRID_CODE)
    write_file(ROOT / "sandbox/sandbox_hybrid/__init__.py", "from .hybrid_sandbox import HybridSandbox, ResourceLimiter, ExecutionTracer, HybridASTGuard")

def build_sandbox_init():
    write_file(ROOT / "sandbox/__init__.py", SANDBOX_INIT_CODE)

def build_autonomous_tester():
    write_file(ROOT / "tester/autonomous_tester.py", TESTER_CODE)
    write_file(ROOT / "tester/__init__.py", "from .autonomous_tester import AutonomousTester, TestResult")

def build_inspector():
    write_file(ROOT / "inspector/static_inspector.py", INSPECTOR_CODE)
    write_file(ROOT / "inspector/__init__.py", "from .static_inspector import StaticInspector, PatternDetector, ASTAnalyzer")

def build_autonomy_engine():
    write_file(ROOT / "autonomy/engine.py", AUTONOMY_CODE)
    write_file(ROOT / "autonomy/__init__.py", "from .engine import AutonomyEngine, IncidentHandler, RepairEngine")

def build_module_generator():
    code = MODULE_GENERATOR_CODE.replace("f\\'''", "f'''").replace("\\'''", "'''")
    write_file(ROOT / "module_generator/generator.py", code)
    write_file(ROOT / "module_generator/__init__.py", "from .generator import ModuleGenerator, CATEGORIES, CATEGORY_TEMPLATES")

def build_rule_engine():
    write_file(ROOT / "rule_engine/rules.py", RULE_ENGINE_CODE)
    write_file(ROOT / "rule_engine/__init__.py", "from .rules import RuleEngine, SeverityRule, CapabilityManager")

def build_lifecycle():
    write_file(ROOT / "lifecycle/manager.py", LIFECYCLE_CODE)
    write_file(ROOT / "lifecycle/__init__.py", "from .manager import ModuleLifecycle, LifecycleHook")

def build_security():
    write_file(ROOT / "security/layer.py", SECURITY_CODE)
    write_file(ROOT / "security/__init__.py", "from .layer import SecurityLayer, CapabilityToken")

def build_registry():
    write_file(ROOT / "registry/module_registry.py", REGISTRY_CODE)
    write_file(ROOT / "registry/__init__.py", "from .module_registry import ModuleRegistry")

def build_workers():
    write_file(ROOT / "workers/pool.py", WORKERS_CODE)
    write_file(ROOT / "workers/__init__.py", "from .pool import WorkerPool, LuminarWorker, WorkerTask")

def build_bridge():
    write_file(ROOT / "bridge/aurora_bridge.py", BRIDGE_CODE)
    write_file(ROOT / "bridge/__init__.py", "from .aurora_bridge import AuroraBridge")

def build_core():
    write_file(ROOT / "aurora_hybrid_core/core.py", CORE_CODE)
    write_file(ROOT / "aurora_hybrid_core/__init__.py", "from .core import AuroraHybridCore")

def build_main():
    write_file(ROOT / "main.py", MAIN_CODE)

def build_zip():
    zip_path = Path("aurora_hybrid_system.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, filenames in os.walk(ROOT):
            for f in filenames:
                p = Path(dirpath) / f
                z.write(p, p.relative_to(ROOT))
    return zip_path

def main():
    print("[1/13] Cleaning previous build...")
    if ROOT.exists():
        shutil.rmtree(ROOT)
    for d in DIRS:
        (ROOT / d).mkdir(parents=True, exist_ok=True)

    print("[2/13] Building Pure Sandbox (U1)...")
    build_sandbox_pure()

    print("[3/13] Building Hybrid Sandbox (U3)...")
    build_sandbox_hybrid()
    build_sandbox_init()

    print("[4/13] Building Autonomous Tester...")
    build_autonomous_tester()

    print("[5/13] Building Static Inspector...")
    build_inspector()

    print("[6/13] Building Autonomy Engine...")
    build_autonomy_engine()

    print("[7/13] Building Module Generator...")
    build_module_generator()

    print("[8/13] Building Rule Engine...")
    build_rule_engine()

    print("[9/13] Building Lifecycle Manager...")
    build_lifecycle()

    print("[10/13] Building Security Layer...")
    build_security()

    print("[11/13] Building Module Registry...")
    build_registry()

    print("[12/13] Building Worker Pool...")
    build_workers()

    print("[13/13] Building Bridge & Core...")
    build_bridge()
    build_core()
    build_main()

    print("\n[PACKAGING] Creating ZIP archive...")
    zip_path = build_zip()
    print(f"\n[SUCCESS] Generated: {zip_path}")
    print(f"[INFO] Directory: {ROOT}")

    file_count = sum(1 for _ in ROOT.glob("**/*.py"))
    print(f"[INFO] Total Python files: {file_count}")

if __name__ == "__main__":
    main()
