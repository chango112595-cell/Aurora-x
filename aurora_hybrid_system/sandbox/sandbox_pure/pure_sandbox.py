import ast
import io
import multiprocessing
import resource
import sys

BLOCKED_MODULES = frozenset(
    [
        "os",
        "subprocess",
        "sys",
        "shutil",
        "socket",
        "ctypes",
        "multiprocessing",
        "threading",
        "signal",
        "resource",
        "importlib",
        "__builtins__",
        "builtins",
        "code",
        "codeop",
        "compile",
        "exec",
        "eval",
        "open",
        "input",
        "breakpoint",
    ]
)

BLOCKED_ATTRS = frozenset(
    [
        "__import__",
        "__loader__",
        "__spec__",
        "__builtins__",
        "__file__",
        "__cached__",
        "__doc__",
        "system",
        "popen",
        "spawn",
        "fork",
        "exec",
        "execv",
        "execve",
        "execl",
    ]
)


class ASTGuard(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split(".")[0] in BLOCKED_MODULES:
                self.violations.append(f"Blocked import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and node.module.split(".")[0] in BLOCKED_MODULES:
            self.violations.append(f"Blocked import from: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in ("exec", "eval", "compile", "open", "__import__"):
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
            "abs": abs,
            "all": all,
            "any": any,
            "bin": bin,
            "bool": bool,
            "chr": chr,
            "dict": dict,
            "divmod": divmod,
            "enumerate": enumerate,
            "filter": filter,
            "float": float,
            "format": format,
            "frozenset": frozenset,
            "getattr": getattr,
            "hasattr": hasattr,
            "hash": hash,
            "hex": hex,
            "int": int,
            "isinstance": isinstance,
            "issubclass": issubclass,
            "iter": iter,
            "len": len,
            "list": list,
            "map": map,
            "max": max,
            "min": min,
            "next": next,
            "oct": oct,
            "ord": ord,
            "pow": pow,
            "print": print,
            "range": range,
            "repr": repr,
            "reversed": reversed,
            "round": round,
            "set": set,
            "slice": slice,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "type": type,
            "zip": zip,
            "True": True,
            "False": False,
            "None": None,
        }
        return {"__builtins__": safe_builtins}

    def _run_in_process(self, code_str, input_data, result_queue):
        try:
            resource.setrlimit(resource.RLIMIT_CPU, (self.cpu_limit_s, self.cpu_limit_s))
            resource.setrlimit(resource.RLIMIT_AS, (self.mem_limit, self.mem_limit))
            try:
                resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
            except (OSError, ValueError):
                pass
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
            try:
                safe_globals = self._create_safe_globals()
                safe_locals = {"input_data": input_data}
                exec(code_str, safe_globals, safe_locals)
                stdout_val = sys.stdout.getvalue()
                stderr_val = sys.stderr.getvalue()
                result = safe_locals.get("result", safe_locals.get("output"))
                result_queue.put(
                    {"ok": True, "stdout": stdout_val, "stderr": stderr_val, "result": result}
                )
            except Exception as e:
                result_queue.put(
                    {
                        "ok": False,
                        "error": f"{type(e).__name__}: {str(e)}",
                        "stdout": sys.stdout.getvalue(),
                        "stderr": sys.stderr.getvalue(),
                    }
                )
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr
        except Exception as e:
            result_queue.put({"ok": False, "error": f"Sandbox error: {str(e)}"})

    def run_code(self, code_str, input_data=None):
        tree, violations = self._guard_ast(code_str)
        if violations:
            return {"ok": False, "error": "AST violations", "violations": violations}
        result_queue = multiprocessing.Queue()
        proc = multiprocessing.Process(
            target=self._run_in_process, args=(code_str, input_data, result_queue)
        )
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
            with open(module_path) as f:
                code = f.read()
            wrapper = (
                code
                + f"\nif callable({entry_func}):\n    result = {entry_func}(input_data)\nelse:\n    result = None"
            )
            return self.run_code(wrapper, payload)
        except FileNotFoundError:
            return {"ok": False, "error": f"Module not found: {module_path}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
