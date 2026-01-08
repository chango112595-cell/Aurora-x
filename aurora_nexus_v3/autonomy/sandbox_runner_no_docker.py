# File: aurora_nexus_v3/autonomy/sandbox_runner_no_docker.py
"""
Containerless Sandbox Runner — Pure Python with optional cgroup isolation.

This module provides secure module execution without Docker dependencies.
Uses resource limits via:
 - cgroups v2 (if available and running as root)
 - resource module (setrlimit) as fallback
 - subprocess timeout as last resort

Works on any Linux system, with degraded isolation on non-Linux platforms.
"""

from __future__ import annotations

import json
import logging
import os
import resource
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("sandbox_runner_no_docker")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)


@dataclass
class SandboxResult:
    """Result of a sandbox execution."""

    ok: bool = False
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    execution_time_ms: float = 0.0
    error: str | None = None
    resource_usage: dict[str, Any] = field(default_factory=dict)


def _check_cgroups_available() -> bool:
    """Check if cgroups v2 is available and we have write access."""
    cgroup_root = Path("/sys/fs/cgroup")
    if not cgroup_root.exists():
        return False
    # Check for cgroups v2 (unified hierarchy)
    if (cgroup_root / "cgroup.controllers").exists():
        # Check if we can create a cgroup
        test_cgroup = cgroup_root / "aurora_sandbox_test"
        try:
            test_cgroup.mkdir(exist_ok=True)
            test_cgroup.rmdir()
            return True
        except PermissionError:
            return False
        except Exception:
            return False
    return False


def _setup_cgroup(cgroup_name: str, mem_mb: int, cpu_seconds: int) -> Path | None:
    """Setup a cgroup for the sandbox. Returns cgroup path or None."""
    cgroup_root = Path("/sys/fs/cgroup")
    cgroup_path = cgroup_root / f"aurora_sandbox_{cgroup_name}"

    try:
        cgroup_path.mkdir(exist_ok=True)

        # Set memory limit
        mem_max = cgroup_path / "memory.max"
        if mem_max.exists():
            mem_max.write_text(str(mem_mb * 1024 * 1024))

        # Set CPU limit (cpu.max format: "$MAX $PERIOD")
        # cpu_seconds is per-second limit, so we use 100000 period (100ms)
        cpu_max = cgroup_path / "cpu.max"
        if cpu_max.exists():
            # Allow cpu_seconds * 100000 microseconds per 100000 period
            quota = min(cpu_seconds * 100000, 100000)
            cpu_max.write_text(f"{quota} 100000")

        return cgroup_path
    except Exception as e:
        logger.warning("Failed to setup cgroup: %s", e)
        return None


def _cleanup_cgroup(cgroup_path: Path) -> None:
    """Clean up a cgroup after use."""
    try:
        if cgroup_path.exists():
            # Kill any remaining processes
            procs_file = cgroup_path / "cgroup.procs"
            if procs_file.exists():
                for pid in procs_file.read_text().strip().split("\n"):
                    if pid:
                        try:
                            os.kill(int(pid), signal.SIGKILL)
                        except (ProcessLookupError, ValueError) as exc:
                            logger.debug("Failed to kill leftover pid %s: %s", pid, exc)
            # Small delay for cleanup
            time.sleep(0.1)
            cgroup_path.rmdir()
    except Exception as e:
        logger.warning("Failed to cleanup cgroup %s: %s", cgroup_path, e)


def _create_sandbox_script(exec_path: Path, input_json: str, cgroup_path: Path | None) -> str:
    """Create a wrapper script that applies resource limits and runs the module."""
    script = f'''#!/usr/bin/env python3
import json
import os
import resource
import sys

# Apply resource limits
try:
    # Memory limit (in bytes)
    mem_limit = {resource.RLIMIT_AS}
    resource.setrlimit(mem_limit, ({256 * 1024 * 1024}, {256 * 1024 * 1024}))
except Exception as exc:
    logger.debug("Failed to apply memory limit: %s", exc)

try:
    # CPU time limit (in seconds)
    cpu_limit = {resource.RLIMIT_CPU}
    resource.setrlimit(cpu_limit, (10, 10))
except Exception as exc:
    logger.debug("Failed to apply CPU limit: %s", exc)

try:
    # File descriptor limit
    nofile = {resource.RLIMIT_NOFILE}
    resource.setrlimit(nofile, (512, 512))
except Exception as exc:
    logger.debug("Failed to apply file descriptor limit: %s", exc)

# Change to module directory
os.chdir("{exec_path.parent}")

# Load input
input_data = {repr(input_json)}

# Import and run the execute module
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("execute_module", "{exec_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["execute_module"] = module
    spec.loader.exec_module(module)

    # Try to find and call the execute function
    if hasattr(module, "execute"):
        result = module.execute(json.loads(input_data))
        print(json.dumps({{"ok": True, "result": result}}))
    elif hasattr(module, "run"):
        result = module.run(json.loads(input_data))
        print(json.dumps({{"ok": True, "result": result}}))
    elif hasattr(module, "main"):
        result = module.main(json.loads(input_data))
        print(json.dumps({{"ok": True, "result": result}}))
    else:
        print(json.dumps({{"ok": True, "result": "module_loaded_no_entry_point"}}))
except Exception as e:
    print(json.dumps({{"ok": False, "error": str(e)}}))
    sys.exit(1)
'''
    return script


def run_module_candidate(
    candidate_dir: Path,
    exec_rel_path: str,
    test_input_json: str,
    resource_limits: dict[str, Any],
    timeout_s: int = 20,
    use_cgroups_if_available: bool = True,
) -> dict[str, Any]:
    """
    Run a module candidate in a sandbox environment.

    Args:
        candidate_dir: Path to the candidate directory
        exec_rel_path: Relative path to the execute file within modules/
        test_input_json: JSON string of test input
        resource_limits: Dict with mem_mb, cpu_seconds, nofile
        timeout_s: Timeout in seconds
        use_cgroups_if_available: Whether to use cgroups if available

    Returns:
        Dict with ok, stdout, stderr, exit_code, execution_time_ms
    """
    modules_dir = candidate_dir / "modules"
    exec_path = modules_dir / exec_rel_path

    if not exec_path.exists():
        return {
            "ok": False,
            "error": f"Execute file not found: {exec_path}",
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "execution_time_ms": 0,
        }

    mem_mb = resource_limits.get("mem_mb", 256)
    cpu_seconds = resource_limits.get("cpu_seconds", 5)
    nofile = resource_limits.get("nofile", 512)

    # Check if cgroups are available
    cgroup_path = None
    if use_cgroups_if_available and _check_cgroups_available():
        cgroup_name = f"{int(time.time() * 1000)}_{os.getpid()}"
        cgroup_path = _setup_cgroup(cgroup_name, mem_mb, cpu_seconds)
        if cgroup_path:
            logger.info("Using cgroups v2 for isolation: %s", cgroup_path)

    # Create temporary script
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        script = _create_sandbox_script(exec_path, test_input_json, cgroup_path)
        f.write(script)
        script_path = f.name

    try:
        start_time = time.perf_counter()

        # Build command
        cmd = [sys.executable, script_path]

        # Set up environment
        env = os.environ.copy()
        env["PYTHONPATH"] = str(modules_dir.parent)

        # Set up preexec_fn to apply resource limits in child
        def preexec():
            try:
                # Memory limit
                resource.setrlimit(resource.RLIMIT_AS, (mem_mb * 1024 * 1024, mem_mb * 1024 * 1024))
            except Exception as exc:
                logger.debug("Failed to apply memory limit in child: %s", exc)
            try:
                # CPU time limit
                resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
            except Exception as exc:
                logger.debug("Failed to apply CPU limit in child: %s", exc)
            try:
                # File descriptor limit
                resource.setrlimit(resource.RLIMIT_NOFILE, (nofile, nofile))
            except Exception as exc:
                logger.debug("Failed to apply nofile limit in child: %s", exc)

            # If cgroup is available, move self into it
            if cgroup_path:
                try:
                    procs_file = cgroup_path / "cgroup.procs"
                    if procs_file.exists():
                        procs_file.write_text(str(os.getpid()))
                except Exception as exc:
                    logger.debug("Failed to assign process to cgroup: %s", exc)

        # Run the process
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout_s,
                env=env,
                cwd=str(modules_dir.parent),
                preexec_fn=preexec if os.name != "nt" else None,
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            stdout = result.stdout.decode("utf-8", errors="replace")
            stderr = result.stderr.decode("utf-8", errors="replace")

            # Try to parse output as JSON
            ok = result.returncode == 0
            try:
                output = json.loads(stdout.strip().split("\n")[-1])
                ok = output.get("ok", ok)
            except (json.JSONDecodeError, IndexError):
                logger.debug("Failed to parse sandbox output as JSON")

            return {
                "ok": ok,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": result.returncode,
                "execution_time_ms": elapsed_ms,
            }

        except subprocess.TimeoutExpired:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return {
                "ok": False,
                "error": f"Timeout after {timeout_s}s",
                "stdout": "",
                "stderr": "",
                "exit_code": -9,
                "execution_time_ms": elapsed_ms,
            }

    finally:
        # Cleanup
        try:
            os.unlink(script_path)
        except Exception as exc:
            logger.debug("Failed to remove sandbox script: %s", exc)

        if cgroup_path:
            _cleanup_cgroup(cgroup_path)


def get_capabilities() -> dict[str, Any]:
    """Get sandbox runner capabilities."""
    cgroups_available = _check_cgroups_available()

    return {
        "runtime": "no_docker",
        "cgroups_available": cgroups_available,
        "resource_limits": ["memory", "cpu", "nofile"],
        "isolation_level": "cgroups" if cgroups_available else "rlimits",
        "platform": sys.platform,
    }


if __name__ == "__main__":
    print(json.dumps(get_capabilities(), indent=2))
