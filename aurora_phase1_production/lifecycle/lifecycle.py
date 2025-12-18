#!/usr/bin/env python3
"""
Aurora Phase-1 Lifecycle Manager
Runtime loader to run module lifecycle (init, execute, cleanup).
"""
import sys
import time
import json
import importlib.util
import traceback
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LifecycleResult:
    module_id: str
    phase: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration_ms: float = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ModuleState:
    module_id: str
    category: str
    status: str = "uninitialized"
    context: Dict = field(default_factory=dict)
    initialized_at: Optional[str] = None
    last_executed: Optional[str] = None
    execution_count: int = 0
    error_count: int = 0


class ModuleLoader:
    """Dynamically load module files"""
    
    def __init__(self, modules_dir: str = None):
        self.modules_dir = Path(modules_dir) if modules_dir else Path(".")
        self.loaded_modules = {}
    
    def load_module(self, module_path: str) -> Optional[Any]:
        """Load a Python module from file path"""
        path = Path(module_path)
        
        if not path.exists():
            full_path = self.modules_dir / module_path
            if full_path.exists():
                path = full_path
            else:
                return None
        
        try:
            module_name = path.stem
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            self.loaded_modules[str(path)] = module
            return module
            
        except Exception as e:
            logger.error(f"Failed to load module {module_path}: {e}")
            return None
    
    def get_entry_point(self, module: Any, entry_point: str) -> Optional[Callable]:
        """Get entry point function from loaded module"""
        if hasattr(module, entry_point):
            func = getattr(module, entry_point)
            if callable(func):
                return func
        return None
    
    def unload_module(self, module_path: str):
        """Unload a previously loaded module"""
        path = str(module_path)
        if path in self.loaded_modules:
            module = self.loaded_modules[path]
            module_name = Path(path).stem
            if module_name in sys.modules:
                del sys.modules[module_name]
            del self.loaded_modules[path]


class ModuleLifecycle:
    """Manage the lifecycle of a single module"""
    
    def __init__(self, module_id: str, category: str, base_dir: str = None):
        self.module_id = module_id
        self.category = category
        self.base_dir = Path(base_dir) if base_dir else Path(".")
        self.loader = ModuleLoader(str(self.base_dir))
        self.state = ModuleState(module_id=module_id, category=category)
        self.results = []
    
    def _get_module_path(self, phase: str) -> Path:
        """Get path to module file for given phase"""
        filename = f"{self.category}_{self.module_id}_{phase}.py"
        return self.base_dir / self.category / filename
    
    def _run_phase(self, phase: str, payload: Any = None, timeout: float = 30.0) -> LifecycleResult:
        """Run a single lifecycle phase"""
        start = time.time()
        module_path = self._get_module_path(phase)
        
        try:
            module = self.loader.load_module(str(module_path))
            if module is None:
                return LifecycleResult(
                    module_id=self.module_id,
                    phase=phase,
                    success=False,
                    error=f"Module not found: {module_path}",
                    duration_ms=(time.time() - start) * 1000
                )
            
            entry_point = self.loader.get_entry_point(module, phase)
            if entry_point is None:
                return LifecycleResult(
                    module_id=self.module_id,
                    phase=phase,
                    success=False,
                    error=f"Entry point '{phase}' not found in module",
                    duration_ms=(time.time() - start) * 1000
                )
            
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(entry_point, payload)
                try:
                    result = future.result(timeout=timeout)
                except FuturesTimeout:
                    return LifecycleResult(
                        module_id=self.module_id,
                        phase=phase,
                        success=False,
                        error="Execution timeout",
                        duration_ms=timeout * 1000
                    )
            
            duration = (time.time() - start) * 1000
            success = True
            error = None
            
            if isinstance(result, dict):
                if result.get("status") == "error":
                    success = False
                    error = result.get("error", "Unknown error")
            
            return LifecycleResult(
                module_id=self.module_id,
                phase=phase,
                success=success,
                result=result,
                error=error,
                duration_ms=duration
            )
            
        except Exception as e:
            return LifecycleResult(
                module_id=self.module_id,
                phase=phase,
                success=False,
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
    
    def init(self, config: Dict = None, timeout: float = 30.0) -> LifecycleResult:
        """Initialize the module"""
        result = self._run_phase("init", config, timeout)
        
        if result.success:
            self.state.status = "initialized"
            self.state.initialized_at = datetime.now(timezone.utc).isoformat()
            self.state.context = result.result if isinstance(result.result, dict) else {}
        else:
            self.state.status = "init_failed"
            self.state.error_count += 1
        
        self.results.append(result)
        return result
    
    def execute(self, payload: Dict = None, timeout: float = 30.0) -> LifecycleResult:
        """Execute the module"""
        if self.state.status not in ["initialized", "executed"]:
            return LifecycleResult(
                module_id=self.module_id,
                phase="execute",
                success=False,
                error=f"Module not initialized (status: {self.state.status})"
            )
        
        result = self._run_phase("execute", payload, timeout)
        
        if result.success:
            self.state.status = "executed"
            self.state.last_executed = datetime.now(timezone.utc).isoformat()
            self.state.execution_count += 1
        else:
            self.state.status = "execute_failed"
            self.state.error_count += 1
        
        self.results.append(result)
        return result
    
    def cleanup(self, context: Dict = None, timeout: float = 30.0) -> LifecycleResult:
        """Cleanup the module"""
        cleanup_ctx = context or self.state.context
        result = self._run_phase("cleanup", cleanup_ctx, timeout)
        
        if result.success:
            self.state.status = "cleaned"
            self.state.context = {}
        else:
            self.state.status = "cleanup_failed"
            self.state.error_count += 1
        
        self.results.append(result)
        return result
    
    def run_full_lifecycle(self, config: Dict = None, payload: Dict = None,
                           timeout: float = 30.0) -> Dict:
        """Run complete lifecycle: init -> execute -> cleanup"""
        results = {
            "module_id": self.module_id,
            "category": self.category,
            "phases": {},
            "success": True,
            "total_duration_ms": 0
        }
        
        init_result = self.init(config, timeout)
        results["phases"]["init"] = asdict(init_result)
        results["total_duration_ms"] += init_result.duration_ms
        
        if not init_result.success:
            results["success"] = False
            results["failed_phase"] = "init"
            return results
        
        execute_result = self.execute(payload, timeout)
        results["phases"]["execute"] = asdict(execute_result)
        results["total_duration_ms"] += execute_result.duration_ms
        
        if not execute_result.success:
            results["success"] = False
            results["failed_phase"] = "execute"
        
        cleanup_result = self.cleanup(timeout=timeout)
        results["phases"]["cleanup"] = asdict(cleanup_result)
        results["total_duration_ms"] += cleanup_result.duration_ms
        
        if not cleanup_result.success:
            results["success"] = results["success"] and False
            if "failed_phase" not in results:
                results["failed_phase"] = "cleanup"
        
        results["final_state"] = asdict(self.state)
        
        return results
    
    def get_state(self) -> Dict:
        """Get current module state"""
        return asdict(self.state)
    
    def get_history(self) -> List[Dict]:
        """Get execution history"""
        return [asdict(r) for r in self.results]


class LifecycleRunner:
    """Run lifecycle operations across multiple modules"""
    
    def __init__(self, modules_dir: str = None, config: Dict = None):
        self.modules_dir = Path(modules_dir) if modules_dir else Path(".")
        self.config = config or {}
        self.lifecycles = {}
        self.execution_log = []
    
    def get_or_create_lifecycle(self, module_id: str, category: str) -> ModuleLifecycle:
        """Get existing lifecycle or create new one"""
        key = f"{category}_{module_id}"
        
        if key not in self.lifecycles:
            self.lifecycles[key] = ModuleLifecycle(
                module_id=module_id,
                category=category,
                base_dir=str(self.modules_dir)
            )
        
        return self.lifecycles[key]
    
    def run_module(self, module_id: str, category: str, 
                   config: Dict = None, payload: Dict = None,
                   timeout: float = 30.0) -> Dict:
        """Run full lifecycle for a single module"""
        lifecycle = self.get_or_create_lifecycle(module_id, category)
        
        result = lifecycle.run_full_lifecycle(config, payload, timeout)
        
        self.execution_log.append({
            "module_id": module_id,
            "category": category,
            "success": result["success"],
            "duration_ms": result["total_duration_ms"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return result
    
    def run_batch(self, modules: List[Dict], workers: int = 4,
                  timeout: float = 30.0) -> List[Dict]:
        """Run lifecycle for multiple modules in parallel"""
        results = []
        
        def run_single(module_spec):
            return self.run_module(
                module_id=module_spec["id"],
                category=module_spec["category"],
                config=module_spec.get("config"),
                payload=module_spec.get("payload"),
                timeout=timeout
            )
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(run_single, m) for m in modules]
            for future in futures:
                try:
                    result = future.result(timeout=timeout * 2)
                    results.append(result)
                except Exception as e:
                    results.append({
                        "success": False,
                        "error": str(e)
                    })
        
        return results
    
    def discover_modules(self, category: str = None) -> List[Dict]:
        """Discover available modules in modules directory"""
        modules = []
        search_dir = self.modules_dir
        
        if category:
            search_dir = search_dir / category
        
        for path in search_dir.rglob("*_execute.py"):
            parts = path.stem.rsplit("_", 1)
            if len(parts) >= 2:
                name_parts = parts[0].rsplit("_", 1)
                if len(name_parts) >= 2:
                    cat = name_parts[0]
                    mod_id = name_parts[1]
                    modules.append({
                        "id": mod_id,
                        "category": cat,
                        "path": str(path.parent)
                    })
        
        return modules
    
    def get_summary(self) -> Dict:
        """Get execution summary"""
        if not self.execution_log:
            return {"total_runs": 0}
        
        total = len(self.execution_log)
        successful = sum(1 for e in self.execution_log if e["success"])
        total_duration = sum(e["duration_ms"] for e in self.execution_log)
        
        by_category = {}
        for entry in self.execution_log:
            cat = entry["category"]
            if cat not in by_category:
                by_category[cat] = {"total": 0, "success": 0}
            by_category[cat]["total"] += 1
            if entry["success"]:
                by_category[cat]["success"] += 1
        
        return {
            "total_runs": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "total_duration_ms": total_duration,
            "avg_duration_ms": total_duration / total if total > 0 else 0,
            "by_category": by_category,
            "active_lifecycles": len(self.lifecycles)
        }
    
    def cleanup_all(self) -> List[LifecycleResult]:
        """Cleanup all active lifecycles"""
        results = []
        
        for key, lifecycle in self.lifecycles.items():
            if lifecycle.state.status in ["initialized", "executed", "execute_failed"]:
                result = lifecycle.cleanup()
                results.append(result)
        
        return results


def create_runner(modules_dir: str = None, config: Dict = None) -> LifecycleRunner:
    return LifecycleRunner(modules_dir=modules_dir, config=config)


if __name__ == "__main__":
    print("Aurora Lifecycle Runner - Test Mode")
    
    runner = LifecycleRunner(modules_dir="generated_modules")
    
    result = runner.run_module(
        module_id="0001",
        category="connector",
        config={"timeout_ms": 5000},
        payload={"action": "test", "data": {"key": "value"}}
    )
    
    print(f"\nLifecycle result:")
    print(f"  Success: {result['success']}")
    print(f"  Duration: {result['total_duration_ms']:.2f}ms")
    
    if result['success']:
        print("\nPhase results:")
        for phase, phase_result in result['phases'].items():
            print(f"  {phase}: {'OK' if phase_result['success'] else 'FAILED'}")
    else:
        print(f"\nFailed at phase: {result.get('failed_phase', 'unknown')}")
        if 'phases' in result:
            for phase, phase_result in result['phases'].items():
                if not phase_result['success']:
                    print(f"  Error: {phase_result.get('error', 'Unknown')}")
    
    print(f"\nSummary: {runner.get_summary()}")
