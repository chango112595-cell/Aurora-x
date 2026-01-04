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
            wrapper = code + f"\nif '{entry}' in dir() and callable({entry}):\n    result = {entry}(input_data)"
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
