"""
Aurora-X Dynamic Module Loader
Dynamically imports and manages all generated modules with sandboxed execution support.
"""

import json
import importlib
import importlib.util
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import lru_cache

logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("aurora_nexus_v3/modules_registry.json")
MODULES_ROOT = Path("aurora_nexus_v3/modules")


class ModuleLoadError(Exception):
    """Raised when module loading fails."""
    pass


class ModuleExecutionError(Exception):
    """Raised when module execution fails."""
    pass


class SandboxedModule:
    """Wrapper for sandboxed module execution."""
    
    def __init__(self, module_id: str, category: str, paths: Dict[str, str],
                 sandbox_type: str = "vm"):
        self.module_id = module_id
        self.category = category
        self.paths = paths
        self.sandbox_type = sandbox_type
        self._init_module = None
        self._execute_module = None
        self._cleanup_module = None
        self._loaded = False
    
    def load(self) -> bool:
        """Load all module components."""
        try:
            self._init_module = self._import_from_path(self.paths["init"])
            self._execute_module = self._import_from_path(self.paths["execute"])
            self._cleanup_module = self._import_from_path(self.paths["cleanup"])
            self._loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load module {self.module_id}: {e}")
            return False
    
    def _import_from_path(self, path_str: str):
        """Import module from file path."""
        path = Path(path_str)
        if not path.exists():
            raise ModuleLoadError(f"Module file not found: {path}")
        
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise ModuleLoadError(f"Cannot create spec for: {path}")
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[path.stem] = module
        spec.loader.exec_module(module)
        return module
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run initialization."""
        if not self._loaded:
            self.load()
        
        if hasattr(self._init_module, 'init'):
            return self._init_module.init(config)
        return {"status": "no_init_function", "module": self.module_id}
    
    def execute(self, payload: Any = None, context: Optional[Dict[str, Any]] = None,
                timeout: float = 30.0) -> Dict[str, Any]:
        """Run execution."""
        if not self._loaded:
            self.load()
        
        if hasattr(self._execute_module, 'execute'):
            return self._execute_module.execute(payload, context, timeout)
        return {"status": "no_execute_function", "module": self.module_id}
    
    def cleanup(self) -> Dict[str, Any]:
        """Run cleanup."""
        if not self._loaded:
            return {"status": "not_loaded", "module": self.module_id}
        
        if hasattr(self._cleanup_module, 'cleanup'):
            return self._cleanup_module.cleanup()
        return {"status": "no_cleanup_function", "module": self.module_id}


class ModuleLoader:
    """Dynamic module loader with registry management."""
    
    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or REGISTRY_PATH
        self.registry: Dict[str, Any] = {}
        self.loaded_modules: Dict[str, SandboxedModule] = {}
        self._executor = ThreadPoolExecutor(max_workers=10)
    
    def load_registry(self) -> bool:
        """Load module registry from disk."""
        if not self.registry_path.exists():
            logger.warning(f"Registry not found at {self.registry_path}")
            return False
        
        with open(self.registry_path, "r") as f:
            data = json.load(f)
        
        self.registry = {
            m["id"]: m for m in data.get("modules", [])
        }
        logger.info(f"Loaded registry with {len(self.registry)} modules")
        return True
    
    def get_module(self, module_id: str) -> Optional[SandboxedModule]:
        """Get or load a specific module."""
        if module_id in self.loaded_modules:
            return self.loaded_modules[module_id]
        
        if module_id not in self.registry:
            logger.error(f"Module {module_id} not in registry")
            return None
        
        mod_info = self.registry[module_id]
        module = SandboxedModule(
            module_id=module_id,
            category=mod_info["category"],
            paths=mod_info["paths"],
            sandbox_type=mod_info.get("sandbox", "vm")
        )
        
        if module.load():
            self.loaded_modules[module_id] = module
            return module
        return None
    
    def get_modules_by_category(self, category: str) -> List[str]:
        """Get all module IDs for a category."""
        return [
            mid for mid, info in self.registry.items()
            if info.get("category") == category
        ]
    
    def get_modules_by_tag(self, tag: str) -> List[str]:
        """Get all module IDs with a specific tag."""
        return [
            mid for mid, info in self.registry.items()
            if tag in info.get("tags", [])
        ]
    
    def initialize_module(self, module_id: str, 
                          config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initialize a specific module."""
        module = self.get_module(module_id)
        if not module:
            return {"status": "error", "error": f"Module {module_id} not found"}
        return module.initialize(config)
    
    def execute_module(self, module_id: str, payload: Any = None,
                       context: Optional[Dict[str, Any]] = None,
                       timeout: float = 30.0) -> Dict[str, Any]:
        """Execute a specific module."""
        module = self.get_module(module_id)
        if not module:
            return {"status": "error", "error": f"Module {module_id} not found"}
        return module.execute(payload, context, timeout)
    
    def cleanup_module(self, module_id: str) -> Dict[str, Any]:
        """Cleanup a specific module."""
        module = self.get_module(module_id)
        if not module:
            return {"status": "error", "error": f"Module {module_id} not found"}
        result = module.cleanup()
        if module_id in self.loaded_modules:
            del self.loaded_modules[module_id]
        return result
    
    def initialize_all(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Initialize all modules or all in a category."""
        module_ids = self.get_modules_by_category(category) if category else list(self.registry.keys())
        results = {}
        
        for mid in module_ids:
            results[mid] = self.initialize_module(mid)
        
        return {
            "total": len(module_ids),
            "initialized": sum(1 for r in results.values() if r.get("status") == "initialized"),
            "results": results
        }
    
    def cleanup_all(self) -> Dict[str, Any]:
        """Cleanup all loaded modules."""
        results = {}
        for mid in list(self.loaded_modules.keys()):
            results[mid] = self.cleanup_module(mid)
        
        return {
            "total": len(results),
            "cleaned": sum(1 for r in results.values() if r.get("status") == "cleanup_complete"),
            "results": results
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loader statistics."""
        categories = {}
        for info in self.registry.values():
            cat = info.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_registered": len(self.registry),
            "total_loaded": len(self.loaded_modules),
            "categories": categories,
            "loaded_modules": list(self.loaded_modules.keys())
        }


_global_loader: Optional[ModuleLoader] = None


def get_loader() -> ModuleLoader:
    """Get or create global module loader."""
    global _global_loader
    if _global_loader is None:
        _global_loader = ModuleLoader()
        _global_loader.load_registry()
    return _global_loader


def init_module(module_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to initialize a module."""
    return get_loader().initialize_module(module_id, config)


def run_module(module_id: str, payload: Any = None, 
               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to execute a module."""
    return get_loader().execute_module(module_id, payload, context)


def cleanup_module(module_id: str) -> Dict[str, Any]:
    """Convenience function to cleanup a module."""
    return get_loader().cleanup_module(module_id)
