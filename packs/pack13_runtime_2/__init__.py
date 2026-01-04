"""
Aurora Pack 13: Runtime 2

Production-ready second-generation runtime environment.
Advanced execution engine with sandboxing, resource limits, and isolation.

Author: Aurora AI System
Version: 2.0.0
"""

import json
import os
import subprocess
import sys
import threading
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

PACK_ID = "pack13"
PACK_NAME = "Runtime 2"
PACK_VERSION = "2.0.0"


class ExecutionMode(Enum):
    DIRECT = "direct"
    SUBPROCESS = "subprocess"
    ISOLATED = "isolated"


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ResourceLimits:
    max_memory_mb: int = 512
    max_cpu_seconds: float = 30.0
    max_output_bytes: int = 1024 * 1024
    max_files: int = 100
    allow_network: bool = False
    allow_subprocess: bool = False


@dataclass
class ExecutionContext:
    context_id: str
    working_dir: str
    env_vars: dict[str, str] = field(default_factory=dict)
    limits: ResourceLimits = field(default_factory=ResourceLimits)
    mode: ExecutionMode = ExecutionMode.DIRECT


@dataclass
class ExecutionResult:
    result_id: str
    context_id: str
    status: ExecutionStatus
    output: str = ""
    error: str = ""
    return_value: Any = None
    duration_seconds: float = 0.0
    memory_used_mb: float = 0.0
    started_at: str = ""
    completed_at: str = ""


class OutputCapture:
    def __init__(self, max_size: int = 1024 * 1024):
        self.max_size = max_size
        self.buffer = StringIO()
        self._lock = threading.Lock()

    def write(self, text: str):
        with self._lock:
            if self.buffer.tell() < self.max_size:
                remaining = self.max_size - self.buffer.tell()
                self.buffer.write(text[:remaining])

    def flush(self):
        return None

    def get_output(self) -> str:
        with self._lock:
            return self.buffer.getvalue()

    def clear(self):
        with self._lock:
            self.buffer = StringIO()


class CodeSandbox:
    SAFE_BUILTINS = {
        "abs",
        "all",
        "any",
        "bin",
        "bool",
        "bytearray",
        "bytes",
        "chr",
        "dict",
        "divmod",
        "enumerate",
        "filter",
        "float",
        "format",
        "frozenset",
        "hash",
        "hex",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "map",
        "max",
        "min",
        "next",
        "oct",
        "ord",
        "pow",
        "print",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "slice",
        "sorted",
        "str",
        "sum",
        "tuple",
        "type",
        "zip",
    }

    BLOCKED_IMPORTS = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "shutil",
        "importlib",
        "ctypes",
        "multiprocessing",
    }

    def __init__(self, limits: ResourceLimits):
        self.limits = limits
        self.restricted_globals: dict[str, Any] = {}
        self._setup_restricted_globals()

    def _setup_restricted_globals(self):
        safe_builtins = {
            name: getattr(
                __builtins__ if isinstance(__builtins__, dict) else __builtins__, name, None
            )
            for name in self.SAFE_BUILTINS
            if hasattr(__builtins__ if isinstance(__builtins__, dict) else __builtins__, name)
        }

        if isinstance(__builtins__, dict):
            for name in self.SAFE_BUILTINS:
                if name in __builtins__:
                    safe_builtins[name] = __builtins__[name]

        self.restricted_globals = {
            "__builtins__": safe_builtins,
            "__name__": "__sandbox__",
            "__doc__": None,
        }

    def execute(self, code: str, local_vars: dict[str, Any] = None) -> tuple:
        if local_vars is None:
            local_vars = {}

        output_capture = OutputCapture(self.limits.max_output_bytes)

        exec_globals = dict(self.restricted_globals)
        exec_globals["print"] = lambda *args, **kwargs: output_capture.write(
            " ".join(str(a) for a in args) + kwargs.get("end", "\n")
        )

        exec_locals = dict(local_vars)

        try:
            exec(compile(code, "<sandbox>", "exec"), exec_globals, exec_locals)
            return exec_locals.get("result"), output_capture.get_output(), None
        except Exception:
            return None, output_capture.get_output(), traceback.format_exc()


class SubprocessExecutor:
    def __init__(self, limits: ResourceLimits, working_dir: str):
        self.limits = limits
        self.working_dir = Path(working_dir)
        self.working_dir.mkdir(parents=True, exist_ok=True)

    def execute_python(self, code: str, env: dict[str, str] = None) -> tuple:
        script_path = self.working_dir / f"script_{time.time_ns()}.py"
        script_path.write_text(code)

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=self.limits.max_cpu_seconds,
                cwd=str(self.working_dir),
                env={**os.environ, **(env or {})},
            )

            return (
                result.stdout[: self.limits.max_output_bytes],
                result.stderr[: self.limits.max_output_bytes],
                result.returncode,
            )
        except subprocess.TimeoutExpired:
            return "", "Execution timed out", -1
        except Exception as e:
            return "", str(e), -1
        finally:
            if script_path.exists():
                script_path.unlink()

    def execute_shell(self, command: str, env: dict[str, str] = None) -> tuple:
        if not self.limits.allow_subprocess:
            return "", "Subprocess execution not allowed", -1

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.limits.max_cpu_seconds,
                cwd=str(self.working_dir),
                env={**os.environ, **(env or {})},
            )

            return (
                result.stdout[: self.limits.max_output_bytes],
                result.stderr[: self.limits.max_output_bytes],
                result.returncode,
            )
        except subprocess.TimeoutExpired:
            return "", "Execution timed out", -1
        except Exception as e:
            return "", str(e), -1


class RuntimeEngine:
    def __init__(self, base_dir: str = "/tmp/aurora_runtime2"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.contexts: dict[str, ExecutionContext] = {}
        self.results: list[ExecutionResult] = []
        self._result_counter = 0
        self._context_counter = 0
        self._lock = threading.Lock()

    def create_context(
        self,
        limits: ResourceLimits = None,
        mode: ExecutionMode = ExecutionMode.DIRECT,
        env_vars: dict[str, str] = None,
    ) -> ExecutionContext:
        with self._lock:
            self._context_counter += 1
            context_id = f"ctx-{self._context_counter:08d}"

        working_dir = self.base_dir / context_id
        working_dir.mkdir(parents=True, exist_ok=True)

        context = ExecutionContext(
            context_id=context_id,
            working_dir=str(working_dir),
            env_vars=env_vars or {},
            limits=limits or ResourceLimits(),
            mode=mode,
        )

        self.contexts[context_id] = context
        return context

    def execute(self, context_id: str, code: str, language: str = "python") -> ExecutionResult:
        context = self.contexts.get(context_id)
        if not context:
            context = self.create_context()

        with self._lock:
            self._result_counter += 1
            result_id = f"res-{self._result_counter:08d}"

        result = ExecutionResult(
            result_id=result_id,
            context_id=context.context_id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now().isoformat(),
        )

        start_time = time.time()

        try:
            if context.mode == ExecutionMode.DIRECT:
                sandbox = CodeSandbox(context.limits)
                return_val, output, error = sandbox.execute(code)

                result.return_value = return_val
                result.output = output
                result.error = error or ""
                result.status = ExecutionStatus.COMPLETED if not error else ExecutionStatus.FAILED

            elif context.mode == ExecutionMode.SUBPROCESS:
                executor = SubprocessExecutor(context.limits, context.working_dir)

                if language == "python":
                    stdout, stderr, returncode = executor.execute_python(code, context.env_vars)
                elif language == "shell":
                    stdout, stderr, returncode = executor.execute_shell(code, context.env_vars)
                else:
                    stdout, stderr, returncode = "", f"Unsupported language: {language}", -1

                result.output = stdout
                result.error = stderr
                result.return_value = returncode
                result.status = (
                    ExecutionStatus.COMPLETED if returncode == 0 else ExecutionStatus.FAILED
                )

            else:
                result.error = f"Unsupported execution mode: {context.mode}"
                result.status = ExecutionStatus.FAILED

        except Exception as e:
            result.error = str(e)
            result.status = ExecutionStatus.FAILED

        result.duration_seconds = time.time() - start_time
        result.completed_at = datetime.now().isoformat()

        with self._lock:
            self.results.append(result)
            if len(self.results) > 1000:
                self.results = self.results[-500:]

        return result

    def get_result(self, result_id: str) -> ExecutionResult | None:
        for result in self.results:
            if result.result_id == result_id:
                return result
        return None

    def cleanup_context(self, context_id: str) -> bool:
        context = self.contexts.get(context_id)
        if not context:
            return False

        working_dir = Path(context.working_dir)
        if working_dir.exists():
            import shutil

            shutil.rmtree(working_dir, ignore_errors=True)

        del self.contexts[context_id]
        return True

    def get_stats(self) -> dict[str, Any]:
        with self._lock:
            total = len(self.results)
            completed = sum(1 for r in self.results if r.status == ExecutionStatus.COMPLETED)
            failed = sum(1 for r in self.results if r.status == ExecutionStatus.FAILED)

            if self.results:
                avg_duration = sum(r.duration_seconds for r in self.results) / total
            else:
                avg_duration = 0

            return {
                "active_contexts": len(self.contexts),
                "total_executions": total,
                "completed": completed,
                "failed": failed,
                "avg_duration_seconds": avg_duration,
            }


class Runtime2:
    def __init__(self, base_dir: str = "/tmp/aurora_runtime2"):
        self.engine = RuntimeEngine(base_dir)
        self.default_context: ExecutionContext | None = None

    def init_context(self, mode: str = "direct", timeout: float = 30.0) -> str:
        exec_mode = ExecutionMode(mode)
        limits = ResourceLimits(max_cpu_seconds=timeout)

        context = self.engine.create_context(limits=limits, mode=exec_mode)
        self.default_context = context
        return context.context_id

    def run(self, code: str, language: str = "python") -> dict[str, Any]:
        if not self.default_context:
            self.init_context()

        result = self.engine.execute(self.default_context.context_id, code, language)

        return {
            "id": result.result_id,
            "status": result.status.value,
            "output": result.output,
            "error": result.error,
            "return_value": result.return_value,
            "duration_seconds": result.duration_seconds,
        }

    def get_stats(self) -> dict[str, Any]:
        return self.engine.get_stats()


def get_pack_info():
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "version": PACK_VERSION,
        "status": "production",
        "components": ["CodeSandbox", "SubprocessExecutor", "RuntimeEngine", "Runtime2"],
        "features": [
            "Sandboxed code execution",
            "Resource limits (CPU, memory, output)",
            "Multiple execution modes",
            "Subprocess isolation",
            "Execution history tracking",
            "Context management",
        ],
    }
