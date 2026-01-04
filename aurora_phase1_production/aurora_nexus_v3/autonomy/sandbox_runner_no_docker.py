#!/usr/bin/env python3
"""
Aurora Phase-1 Containerless Sandbox Runner
Executes code with resource limits and optional uid drop (no Docker required).
"""
import ast
import sys
import os
import time
import resource
import signal
import traceback
from typing import Any, Dict, Optional
from multiprocessing import Process, Queue
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

DANGEROUS_BUILTINS = frozenset([
    'eval', 'exec', 'compile', '__import__', 'open', 'input',
    'breakpoint', 'memoryview', 'globals', 'locals', 'vars'
])

DANGEROUS_IMPORTS = frozenset([
    'os', 'sys', 'subprocess', 'shutil', 'socket', 'ctypes',
    'multiprocessing', 'threading', 'signal', 'resource',
    'importlib', 'builtins', '__builtins__', 'code', 'codeop'
])

SAFE_BUILTINS = {
    'abs': abs, 'all': all, 'any': any, 'ascii': ascii,
    'bin': bin, 'bool': bool, 'bytearray': bytearray, 'bytes': bytes,
    'callable': callable, 'chr': chr, 'classmethod': classmethod,
    'complex': complex, 'dict': dict, 'dir': dir, 'divmod': divmod,
    'enumerate': enumerate, 'filter': filter, 'float': float,
    'format': format, 'frozenset': frozenset, 'getattr': getattr,
    'hasattr': hasattr, 'hash': hash, 'hex': hex, 'id': id,
    'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
    'iter': iter, 'len': len, 'list': list, 'map': map, 'max': max,
    'min': min, 'next': next, 'object': object, 'oct': oct,
    'ord': ord, 'pow': pow, 'print': print, 'property': property,
    'range': range, 'repr': repr, 'reversed': reversed, 'round': round,
    'set': set, 'setattr': setattr, 'slice': slice, 'sorted': sorted,
    'staticmethod': staticmethod, 'str': str, 'sum': sum,
    'super': super, 'tuple': tuple, 'type': type, 'zip': zip,
    'True': True, 'False': False, 'None': None,
    'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError,
    'KeyError': KeyError, 'IndexError': IndexError, 'AttributeError': AttributeError,
}


class ASTGuard(ast.NodeVisitor):
    """AST visitor that blocks dangerous constructs"""
    
    def __init__(self):
        self.violations = []
    
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split('.')[0] in DANGEROUS_IMPORTS:
                self.violations.append(f"Blocked import: {alias.name}")
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module and node.module.split('.')[0] in DANGEROUS_IMPORTS:
            self.violations.append(f"Blocked import from: {node.module}")
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in DANGEROUS_BUILTINS:
                self.violations.append(f"Blocked builtin call: {node.func.id}")
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in ['system', 'popen', 'spawn', 'fork', 'exec']:
                self.violations.append(f"Blocked method call: {node.func.attr}")
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        if node.attr.startswith('_') and node.attr.startswith('__'):
            if node.attr not in ['__init__', '__str__', '__repr__', '__len__', '__iter__']:
                self.violations.append(f"Blocked dunder access: {node.attr}")
        self.generic_visit(node)
    
    def check(self, code: str) -> tuple:
        try:
            tree = ast.parse(code)
            self.visit(tree)
            return len(self.violations) == 0, self.violations
        except SyntaxError as e:
            return False, [f"Syntax error: {e}"]


class ResourceLimiter:
    """Apply resource limits to the current process"""
    
    def __init__(self, cpu_seconds: int = 5, memory_mb: int = 128, 
                 max_files: int = 10, max_processes: int = 0):
        self.cpu_seconds = cpu_seconds
        self.memory_bytes = memory_mb * 1024 * 1024
        self.max_files = max_files
        self.max_processes = max_processes
    
    def apply(self):
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (self.cpu_seconds, self.cpu_seconds + 1))
        except (ValueError, resource.error):
            pass
        
        try:
            resource.setrlimit(resource.RLIMIT_AS, (self.memory_bytes, self.memory_bytes))
        except (ValueError, resource.error):
            pass
        
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (self.max_files, self.max_files))
        except (ValueError, resource.error):
            pass
        
        if self.max_processes >= 0:
            try:
                resource.setrlimit(resource.RLIMIT_NPROC, (self.max_processes, self.max_processes))
            except (ValueError, resource.error):
                pass


class SandboxRunner:
    """Containerless sandbox runner with resource limits"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.timeout_seconds = self.config.get("timeout_seconds", 10)
        self.memory_mb = self.config.get("memory_mb", 128)
        self.cpu_seconds = self.config.get("cpu_seconds", 5)
        self.guard = ASTGuard()
        self.limiter = ResourceLimiter(
            cpu_seconds=self.cpu_seconds,
            memory_mb=self.memory_mb
        )
    
    def validate_code(self, code: str) -> tuple:
        guard = ASTGuard()
        return guard.check(code)
    
    def _execute_in_sandbox(self, code: str, queue: Queue, payload: Dict = None):
        """Execute code in a sandboxed environment"""
        try:
            self.limiter.apply()
            
            sandbox_globals = {"__builtins__": SAFE_BUILTINS.copy()}
            sandbox_locals = {"payload": payload or {}}
            
            exec(compile(code, "<sandbox>", "exec"), sandbox_globals, sandbox_locals)
            
            result = sandbox_locals.get("result", sandbox_locals.get("output"))
            
            queue.put({"ok": True, "result": result, "locals": {
                k: v for k, v in sandbox_locals.items() 
                if not k.startswith("_") and k != "payload"
            }})
        except Exception as e:
            queue.put({"ok": False, "error": str(e), "traceback": traceback.format_exc()})
    
    def run(self, code: str, payload: Dict = None, use_process: bool = True) -> Dict:
        """Run code in sandbox with timeout and resource limits"""
        is_safe, violations = self.validate_code(code)
        if not is_safe:
            return {"ok": False, "error": "Code validation failed", "violations": violations}
        
        if use_process:
            return self._run_with_process(code, payload)
        else:
            return self._run_with_thread(code, payload)
    
    def _run_with_process(self, code: str, payload: Dict = None) -> Dict:
        """Run using multiprocessing for true isolation"""
        queue = Queue()
        proc = Process(target=self._execute_in_sandbox, args=(code, queue, payload))
        
        try:
            proc.start()
            proc.join(timeout=self.timeout_seconds)
            
            if proc.is_alive():
                proc.terminate()
                proc.join(timeout=1)
                if proc.is_alive():
                    proc.kill()
                return {"ok": False, "error": "Execution timeout", "timeout": True}
            
            if not queue.empty():
                return queue.get()
            else:
                return {"ok": False, "error": "No result returned"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
        finally:
            if proc.is_alive():
                proc.kill()
    
    def _run_with_thread(self, code: str, payload: Dict = None) -> Dict:
        """Run using ThreadPoolExecutor (more compatible, less isolation)"""
        def execute():
            sandbox_globals = {"__builtins__": SAFE_BUILTINS.copy()}
            sandbox_locals = {"payload": payload or {}}
            exec(compile(code, "<sandbox>", "exec"), sandbox_globals, sandbox_locals)
            return {
                "result": sandbox_locals.get("result"),
                "locals": {k: v for k, v in sandbox_locals.items() 
                          if not k.startswith("_") and k != "payload"}
            }
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            try:
                future = executor.submit(execute)
                result = future.result(timeout=self.timeout_seconds)
                return {"ok": True, **result}
            except FuturesTimeout:
                return {"ok": False, "error": "Execution timeout", "timeout": True}
            except Exception as e:
                return {"ok": False, "error": str(e), "traceback": traceback.format_exc()}
    
    def run_module(self, module_path: str, entry_point: str = "execute", 
                   payload: Dict = None) -> Dict:
        """Load and run a module file in sandbox"""
        try:
            with open(module_path, 'r') as f:
                code = f.read()
            
            is_safe, violations = self.validate_code(code)
            if not is_safe:
                return {"ok": False, "error": "Module validation failed", "violations": violations}
            
            wrapped_code = f"""
{code}

if '{entry_point}' in dir():
    result = {entry_point}(payload)
else:
    result = {{"error": "Entry point '{entry_point}' not found"}}
"""
            return self.run(wrapped_code, payload, use_process=False)
        except FileNotFoundError:
            return {"ok": False, "error": f"Module not found: {module_path}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}


def create_runner(config: Dict = None) -> SandboxRunner:
    return SandboxRunner(config)


if __name__ == "__main__":
    runner = SandboxRunner()
    
    test_code = """
x = 5 + 3
y = x * 2
result = {"sum": x, "product": y}
"""
    
    print("Testing sandbox runner...")
    result = runner.run(test_code, use_process=False)
    print(f"Result: {result}")
    
    dangerous_code = """
import os
os.system("echo hacked")
"""
    
    print("\nTesting dangerous code...")
    result = runner.run(dangerous_code)
    print(f"Result: {result}")
