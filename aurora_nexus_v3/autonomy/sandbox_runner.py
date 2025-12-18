"""
Aurora-X Sandbox Runner
Container-per-module sandbox execution with cgroup fallback.
"""

import os
import sys
import time
import json
import logging
import subprocess
import resource
import signal
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FuturesTimeout
import multiprocessing

logger = logging.getLogger(__name__)


class SandboxType(Enum):
    """Types of sandbox environments."""
    NONE = "none"
    CGROUP = "cgroup"
    CONTAINER = "container"
    VM = "vm"
    WASM = "wasm"


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution."""
    sandbox_type: SandboxType = SandboxType.CGROUP
    memory_limit_mb: int = 256
    cpu_limit_percent: int = 50
    timeout_seconds: int = 30
    network_enabled: bool = False
    filesystem_readonly: bool = True
    allowed_paths: Optional[List[str]] = None
    env_vars: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.allowed_paths is None:
            self.allowed_paths = []
        if self.env_vars is None:
            self.env_vars = {}


@dataclass
class SandboxResult:
    """Result from sandbox execution."""
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time_ms: float = 0
    memory_used_mb: float = 0
    exit_code: int = 0


class CgroupSandbox:
    """cgroup-based sandbox for resource limiting."""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self._cgroup_available = self._check_cgroup_support()
    
    def _check_cgroup_support(self) -> bool:
        """Check if cgroups are available."""
        return Path("/sys/fs/cgroup").exists()
    
    def _set_resource_limits(self):
        """Set resource limits using setrlimit."""
        memory_bytes = self.config.memory_limit_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        
        cpu_time = self.config.timeout_seconds
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_time, cpu_time))
        
        resource.setrlimit(resource.RLIMIT_NPROC, (50, 50))
        resource.setrlimit(resource.RLIMIT_NOFILE, (100, 100))
    
    def execute(self, func: Callable, *args, **kwargs) -> SandboxResult:
        """Execute function in sandbox."""
        start_time = time.time()
        
        def sandboxed_run():
            self._set_resource_limits()
            return func(*args, **kwargs)
        
        try:
            with ProcessPoolExecutor(max_workers=1) as executor:
                future = executor.submit(sandboxed_run)
                result = future.result(timeout=self.config.timeout_seconds)
            
            return SandboxResult(
                success=True,
                output=result,
                execution_time_ms=(time.time() - start_time) * 1000
            )
            
        except FuturesTimeout:
            return SandboxResult(
                success=False,
                output=None,
                error="Execution timeout",
                execution_time_ms=(time.time() - start_time) * 1000
            )
        except MemoryError:
            return SandboxResult(
                success=False,
                output=None,
                error="Memory limit exceeded"
            )
        except Exception as e:
            return SandboxResult(
                success=False,
                output=None,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )


class ContainerSandbox:
    """Container-based sandbox using Docker/Podman."""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self._runtime = self._detect_runtime()
    
    def _detect_runtime(self) -> Optional[str]:
        """Detect available container runtime."""
        for runtime in ["podman", "docker"]:
            try:
                subprocess.run([runtime, "--version"], 
                             capture_output=True, check=True)
                return runtime
            except:
                pass
        return None
    
    def execute(self, module_path: str, payload: Dict[str, Any]) -> SandboxResult:
        """Execute module in container."""
        if not self._runtime:
            logger.warning("No container runtime, falling back to cgroup")
            return CgroupSandbox(self.config).execute(
                lambda: {"error": "Container runtime not available"}
            )
        
        start_time = time.time()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            payload_file = Path(tmpdir) / "payload.json"
            payload_file.write_text(json.dumps(payload))
            
            cmd = [
                self._runtime, "run", "--rm",
                "-m", f"{self.config.memory_limit_mb}m",
                "--cpus", str(self.config.cpu_limit_percent / 100),
                "-v", f"{tmpdir}:/data:ro",
                "-v", f"{module_path}:/module:ro",
            ]
            
            if not self.config.network_enabled:
                cmd.extend(["--network", "none"])
            
            cmd.extend([
                "python:3.11-slim",
                "python", "/module", "--payload", "/data/payload.json"
            ])
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=self.config.timeout_seconds,
                    text=True
                )
                
                return SandboxResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr if result.returncode != 0 else None,
                    execution_time_ms=(time.time() - start_time) * 1000,
                    exit_code=result.returncode
                )
                
            except subprocess.TimeoutExpired:
                return SandboxResult(
                    success=False,
                    output=None,
                    error="Container execution timeout",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            except Exception as e:
                return SandboxResult(
                    success=False,
                    output=None,
                    error=str(e)
                )


class SandboxRunner:
    """
    Main sandbox runner that selects appropriate sandbox type.
    Supports container, cgroup, and fallback modes.
    """
    
    def __init__(self, default_config: Optional[SandboxConfig] = None):
        self.default_config = default_config or SandboxConfig()
        self._cgroup_sandbox = CgroupSandbox(self.default_config)
        self._container_sandbox = ContainerSandbox(self.default_config)
    
    def get_sandbox(self, sandbox_type: SandboxType, 
                    config: Optional[SandboxConfig] = None):
        """Get appropriate sandbox for type."""
        cfg = config or self.default_config
        
        if sandbox_type == SandboxType.CONTAINER:
            return ContainerSandbox(cfg)
        elif sandbox_type in (SandboxType.CGROUP, SandboxType.VM):
            return CgroupSandbox(cfg)
        else:
            return CgroupSandbox(cfg)
    
    def run_module(self, module_id: str, module_path: str,
                   payload: Any = None, context: Optional[Dict[str, Any]] = None,
                   sandbox_type: SandboxType = SandboxType.CGROUP,
                   config: Optional[SandboxConfig] = None) -> SandboxResult:
        """Run a module in sandbox."""
        cfg = config or self.default_config
        
        logger.info(f"Running module {module_id} in {sandbox_type.value} sandbox")
        
        if sandbox_type == SandboxType.CONTAINER:
            return self._container_sandbox.execute(
                module_path, 
                {"payload": payload, "context": context or {}}
            )
        else:
            return self._run_with_cgroup(module_path, payload, context, cfg)
    
    def _run_with_cgroup(self, module_path: str, payload: Any,
                         context: Optional[Dict[str, Any]],
                         config: SandboxConfig) -> SandboxResult:
        """Run module with cgroup limits."""
        sandbox = CgroupSandbox(config)
        
        def execute_module():
            import importlib.util
            
            spec = importlib.util.spec_from_file_location("module", module_path)
            if spec is None or spec.loader is None:
                return {"error": f"Cannot load module from {module_path}"}
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'execute'):
                return module.execute(payload, context)
            return {"error": "No execute function found"}
        
        return sandbox.execute(execute_module)
    
    def run_batch(self, modules: List[Dict[str, Any]],
                  max_parallel: int = 4) -> Dict[str, SandboxResult]:
        """Run multiple modules in parallel sandboxes."""
        results = {}
        
        with ProcessPoolExecutor(max_workers=max_parallel) as executor:
            futures = {}
            
            for mod in modules:
                future = executor.submit(
                    self.run_module,
                    mod["id"],
                    mod["path"],
                    mod.get("payload"),
                    mod.get("context"),
                    SandboxType(mod.get("sandbox", "cgroup"))
                )
                futures[future] = mod["id"]
            
            for future in futures:
                module_id = futures[future]
                try:
                    results[module_id] = future.result(timeout=60)
                except Exception as e:
                    results[module_id] = SandboxResult(
                        success=False,
                        output=None,
                        error=str(e)
                    )
        
        return results
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get sandbox capabilities."""
        container_available = self._container_sandbox._runtime is not None
        cgroup_available = self._cgroup_sandbox._cgroup_available
        
        return {
            "container_runtime": self._container_sandbox._runtime,
            "container_available": container_available,
            "cgroup_available": cgroup_available,
            "default_sandbox": self.default_config.sandbox_type.value,
            "supported_types": [t.value for t in SandboxType]
        }


# Module-level singleton and function for prod_autonomy.py compatibility
_default_runner: Optional[SandboxRunner] = None


def _get_runner() -> SandboxRunner:
    """Get or create the default sandbox runner."""
    global _default_runner
    if _default_runner is None:
        _default_runner = SandboxRunner()
    return _default_runner


def run_module_candidate(
    candidate_dir: Path,
    exec_rel_path: str,
    test_input_json: str,
    resource_limits: Dict[str, Any],
    timeout_s: int = 30,
    image: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a module candidate in a sandbox.
    
    Args:
        candidate_dir: Path to the candidate directory
        exec_rel_path: Relative path to the execute file within modules/
        test_input_json: JSON string of test input
        resource_limits: Dict with mem_mb and cpus
        timeout_s: Timeout in seconds
        image: Optional Docker image to use
    
    Returns:
        Dict with ok, stdout, stderr, exit_code
    """
    runner = _get_runner()
    
    modules_dir = candidate_dir / "modules"
    exec_path = modules_dir / exec_rel_path
    
    if not exec_path.exists():
        return {"ok": False, "error": f"Execute file not found: {exec_path}"}
    
    config = SandboxConfig(
        memory_limit_mb=resource_limits.get("mem_mb", 256),
        cpu_limit_percent=int(resource_limits.get("cpus", 0.5) * 100),
        timeout_seconds=timeout_s
    )
    
    try:
        payload = json.loads(test_input_json)
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"Invalid JSON input: {e}"}
    
    result = runner.run_module(
        module_id=exec_rel_path,
        module_path=str(exec_path),
        payload=payload,
        sandbox_type=SandboxType.CONTAINER if image else SandboxType.CGROUP,
        config=config
    )
    
    return {
        "ok": result.success,
        "stdout": str(result.output) if result.output else "",
        "stderr": result.error or "",
        "exit_code": result.exit_code,
        "execution_time_ms": result.execution_time_ms
    }
