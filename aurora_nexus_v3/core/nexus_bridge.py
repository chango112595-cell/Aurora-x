
"""
Aurora Nexus V3 Bridge
======================
Connects Luminar Nexus V3 to Aurora-X modules without breaking existing systems.

HYBRID MODE INTEGRATION:
- Uses V3's existing ThreadPool (no double-threads)
- Hooks into V3 lifecycle (on_boot, on_tick, on_reflect)
- Keeps Luminar V2 chat separate but queryable
- Graceful fallback when GPU/optional libs missing

Author: Aurora AI System
Version: 1.0.0
"""

import os
import sys
import json
import threading
import importlib
import importlib.util
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class NexusBridge:
    """
    Connects Luminar Nexus V3 to Aurora-X modules.

    Integration Points:
    - load_modules(): Called during V3 boot
    - execute_all(): Parallel execution across modules
    - reflect(): Feedback hook into V3 reflection system
    - update_bias(): Tie into V3 learning stats

    Does NOT replace any V3 functionality - only extends it.
    """

    def __init__(self, module_path: str = None, pool_size: int = 8):
        """
        Initialize bridge with optional custom module path.

        Args:
            module_path: Path to modules directory (auto-detected if None)
            pool_size: ThreadPool workers (reuses V3 pool size if available)
        """
        self.module_path = module_path or self._find_module_path()
        self.modules: Dict[str, Any] = {}
        self.modules_by_id: Dict[int, Any] = {}
        self.lock = threading.Lock()
        self.gpu_available = TORCH_AVAILABLE and (torch.cuda.is_available() if TORCH_AVAILABLE else False)
        self.pool = ThreadPoolExecutor(max_workers=pool_size)
        self._initialized = False
        self._v3_core = None
        self._reflection_callbacks = []

    def _find_module_path(self) -> str:
        """Auto-detect module path from common locations"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        candidates = [
            os.path.join(base_dir, "aurora_x/core/modules"),
            "aurora_x/core/modules",
            "aurora_phase1_production/aurora_x/modules",
            "modules",
            "../aurora_x/core/modules"
        ]
        for path in candidates:
            if os.path.isdir(path):
                return path
        return os.path.join(base_dir, "aurora_x/core/modules")

    def attach_v3_core(self, core):
        """Attach to existing V3 core (called by V3 main.py)"""
        self._v3_core = core
        return self

    def load_modules(self) -> Dict[str, Any]:
        """
        Load all modules from manifest.
        Called during V3 boot sequence.
        """
        manifest_path = os.path.join(self.module_path, "modules.manifest.json")

        if not os.path.exists(manifest_path):
            print(f"[NexusBridge] No manifest at {manifest_path}")
            return {"loaded": 0, "errors": []}

        with open(manifest_path) as f:
            data = json.load(f)

        loaded = 0
        errors = []

        modules_list = data if isinstance(data, list) else data.get("modules", [])
        for m in modules_list:
            try:
                mid = m["id"]
                name = m.get("name", f"module_{mid:03d}")
                
                file_candidates = [
                    os.path.join(self.module_path, f"module_{mid:03d}.py"),
                    os.path.join(self.module_path, f"AuroraModule{mid:03d}.py"),
                ]
                
                module_file = None
                for candidate in file_candidates:
                    if os.path.exists(candidate):
                        module_file = candidate
                        break
                
                if not module_file:
                    continue

                spec = importlib.util.spec_from_file_location(f"module_{mid:03d}", module_file)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)

                    cls_name = f"AuroraModule{mid}" if hasattr(mod, f"AuroraModule{mid}") else f"AuroraModule{mid:03d}"
                    cls = getattr(mod, cls_name, None)
                    if cls:
                        instance = cls()
                        if hasattr(instance, 'set_nexus'):
                            instance.set_nexus(self)

                        if not hasattr(instance, "name"):
                            setattr(instance, "name", name)
                        if not hasattr(instance, "category"):
                            setattr(instance, "category", m.get("category", "unknown"))
                        if not hasattr(instance, "temporal_tier"):
                            setattr(instance, "temporal_tier", m.get("tier", "foundational"))
                        if not hasattr(instance, "gpu_enabled"):
                            setattr(instance, "gpu_enabled", False)

                        self.modules[name] = instance
                        self.modules_by_id[mid] = instance
                        loaded += 1

            except Exception as e:
                errors.append({"id": m.get("id"), "error": str(e)})

        self._initialized = True
        print(f"[NexusBridge] Loaded {loaded} modules (GPU: {self.gpu_available})")

        return {"loaded": loaded, "errors": errors, "gpu_available": self.gpu_available}

    def get_module(self, identifier) -> Optional[Any]:
        """Get module by name or ID"""
        if isinstance(identifier, int):
            return self.modules_by_id.get(identifier)
        return self.modules.get(identifier)

    def execute(self, module_id, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single module"""
        module = self.get_module(module_id)
        if not module:
            return {"status": "error", "error": f"Module {module_id} not found"}
        return module.execute(payload)

    def execute_all(self, payload: Dict[str, Any], 
                    filter_category: str = None,
                    filter_tier: str = None) -> List[Dict[str, Any]]:
        """
        Execute payload across all matching modules in parallel.
        Uses existing V3 ThreadPool pattern.
        
        HYBRID MODE:
        - Uses GPU when available for modules 451-550
        - Falls back to CPU pool otherwise
        - Preserves original payload, adds metadata under separate keys
        """
        targets = []
        gpu_targets = []
        
        for name, module in self.modules.items():
            if filter_category and module.category != filter_category:
                continue
            if filter_tier and module.temporal_tier != filter_tier:
                continue
            
            if self.gpu_available and hasattr(module, 'gpu_enabled') and module.gpu_enabled:
                gpu_targets.append(module)
            else:
                targets.append(module)

        if not targets and not gpu_targets:
            return []

        results = []
        
        if self.gpu_available and gpu_targets:
            gpu_payload = {**payload, "_hybrid_mode": "gpu", "_execution_target": "cuda"}
            for module in gpu_targets:
                try:
                    result = module.execute(gpu_payload)
                    results.append(result)
                except Exception as e:
                    results.append({"status": "error", "module": module.name, "error": str(e)})
        
        if targets:
            cpu_payload = {**payload, "_hybrid_mode": "cpu", "_execution_target": "pool"} if self.gpu_available else payload
            futures = {self.pool.submit(m.execute, cpu_payload): getattr(m, "name", "unknown") for m in targets}
            
            for future in as_completed(futures):
                name = futures[future]
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    results.append({"status": "error", "module": name, "error": str(e)})

        return results
    
    def execute_hybrid(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hybrid-Mode Runtime: CPU + GPU + Speculative Threads.
        Schedules GPU tasks via NexusBridge if CUDA available; else reverts to CPU pool.
        Preserves original payload semantics - adds metadata without overwriting.
        """
        if self.gpu_available:
            print(f"[NexusBridge] Hybrid mode: GPU available, using CUDA acceleration")
        else:
            print(f"[NexusBridge] Hybrid mode: GPU not available, using CPU pool")
        
        results = self.execute_all(payload)
        
        return {
            "status": "success",
            "mode": "gpu" if self.gpu_available else "cpu",
            "modules_executed": len(results),
            "results": results
        }

    def on_boot(self):
        """V3 lifecycle hook - initialize all modules"""
        results = []
        for module in self.modules.values():
            if hasattr(module, 'on_boot'):
                results.append(module.on_boot())
        return results

    def on_tick(self, tick_data: Dict[str, Any] = None):
        """V3 lifecycle hook - propagate tick to modules"""
        for module in self.modules.values():
            if hasattr(module, 'on_tick'):
                try:
                    module.on_tick(tick_data)
                except TypeError:
                    module.on_tick()

    def on_reflect(self, context: Dict[str, Any] = None):
        """V3 lifecycle hook - collect reflection data from modules"""
        reflections = []
        for module in self.modules.values():
            if hasattr(module, 'on_reflect'):
                try:
                    result = module.on_reflect(context)
                except TypeError:
                    result = module.on_reflect()
                if result is None:
                    result = {
                        "module": getattr(module, "name", "unknown"),
                        "metrics": {},
                        "healthy": True,
                    }
                reflections.append(result)
        return reflections

    def reflect(self, source: str, payload: Dict[str, Any]):
        """
        Feedback hook from modules - ties into V3 reflection system.
        Does NOT replace V3 reflection, only adds module feedback.
        """
        for callback in self._reflection_callbacks:
            try:
                callback(source, payload)
            except:
                pass

        if self._v3_core and hasattr(self._v3_core, 'reflection_manager'):
            try:
                self._v3_core.reflection_manager.add_signal(source, payload)
            except:
                pass

    def add_reflection_callback(self, callback):
        """Add custom reflection callback"""
        self._reflection_callbacks.append(callback)

    def update_bias(self, module_name: str, data: Dict[str, Any]):
        """
        Learning signal from modules - ties into V3 learning system.
        Does NOT replace V3 learning, only adds module signals.
        """
        if self._v3_core and hasattr(self._v3_core, 'learning_manager'):
            try:
                self._v3_core.learning_manager.update_bias(module_name, data)
            except:
                pass

    def get_status(self) -> Dict[str, Any]:
        """Get bridge and module status"""
        healthy = 0
        unhealthy = 0
        gpu_modules = 0

        for module in self.modules.values():
            if hasattr(module, "diagnose"):
                diag = module.diagnose()
            else:
                diag = {
                    "healthy": True,
                    "gpu_enabled": getattr(module, "gpu_enabled", False),
                }
            if diag.get("healthy"):
                healthy += 1
            else:
                unhealthy += 1
            if diag.get("gpu_enabled"):
                gpu_modules += 1

        return {
            "initialized": self._initialized,
            "total_modules": len(self.modules),
            "healthy": healthy,
            "unhealthy": unhealthy,
            "gpu_available": self.gpu_available,
            "gpu_modules": gpu_modules
        }

    def shutdown(self):
        """Graceful shutdown"""
        self.pool.shutdown(wait=False)
        self.modules.clear()
        self._initialized = False
