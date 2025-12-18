#!/usr/bin/env python3
"""
Aurora Phase-1 Module Generator Helpers
Candidate generation, snapshot management, and promote operations.
"""
import os
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    module_id: str
    category: str
    driver: str
    files: List[str] = field(default_factory=list)
    success: bool = True
    error: Optional[str] = None
    checksum: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class SnapshotInfo:
    module_id: str
    snapshot_path: str
    original_path: str
    version: int
    checksum: str
    created: str


@dataclass
class PromoteResult:
    module_id: str
    category: str
    promoted: bool
    files_promoted: List[str] = field(default_factory=list)
    snapshots_created: List[str] = field(default_factory=list)
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CodeTemplates:
    """Code generation templates for different module categories"""
    
    @staticmethod
    def get_init_template(category: str, module_id: str, driver: str) -> str:
        class_name = f"{category.title()}_{module_id}"
        
        return f'''"""
Aurora Module: {category}_{module_id}
Category: {category}
Driver: {driver}
Type: init
Generated: {datetime.now(timezone.utc).isoformat()}
"""


class {class_name}Init:
    """Initialize {category} module with driver: {driver}"""
    
    def __init__(self, config=None):
        self.config = config or {{}}
        self.driver = "{driver}"
        self.initialized = False
        self.timeout = self.config.get("timeout_ms", 30000)
        self.retry_count = self.config.get("retry_count", 3)
        self.buffer_size = self.config.get("buffer_size", 8192)
        self.context = {{}}
    
    def init(self):
        """Initialize module resources"""
        try:
            self.context = self._setup_context()
            self.initialized = True
            return {{
                "status": "initialized",
                "driver": self.driver,
                "category": "{category}",
                "context": self.context
            }}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}
    
    def _setup_context(self):
        """Setup module context"""
        return {{
            "driver": self.driver,
            "buffer": [],
            "connections": [],
            "state": "ready"
        }}
    
    def get_context(self):
        """Return current context"""
        return self.context


def init(config=None):
    """Module entry point for initialization"""
    instance = {class_name}Init(config)
    return instance.init()
'''
    
    @staticmethod
    def get_execute_template(category: str, module_id: str, driver: str) -> str:
        class_name = f"{category.title()}_{module_id}"
        
        return f'''"""
Aurora Module: {category}_{module_id}
Category: {category}
Driver: {driver}
Type: execute
Generated: {datetime.now(timezone.utc).isoformat()}
"""
import time
import hashlib
from typing import Dict, Any, Optional


class {class_name}Execute:
    """Execute {category} module operations"""
    
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.driver = "{driver}"
        self.metrics = {{
            "executions": 0,
            "total_duration_ms": 0,
            "errors": 0
        }}
    
    def execute(self, payload: Dict = None) -> Dict:
        """Main execution entry point"""
        start = time.time()
        payload = payload or {{}}
        
        try:
            action = payload.get("action", "default")
            data = payload.get("data", {{}})
            options = payload.get("options", {{}})
            
            result = self._dispatch(action, data, options)
            
            duration = (time.time() - start) * 1000
            self.metrics["executions"] += 1
            self.metrics["total_duration_ms"] += duration
            
            return {{
                "status": "ok",
                "driver": self.driver,
                "action": action,
                "result": result,
                "duration_ms": duration,
                "execution_id": self._generate_id(payload)
            }}
        except Exception as e:
            self.metrics["errors"] += 1
            return {{
                "status": "error",
                "error": str(e),
                "duration_ms": (time.time() - start) * 1000
            }}
    
    def _dispatch(self, action: str, data: Dict, options: Dict) -> Dict:
        """Dispatch to appropriate handler based on action"""
        handlers = {{
            "default": self._handle_default,
            "process": self._handle_process,
            "transform": self._handle_transform,
            "validate": self._handle_validate,
            "query": self._handle_query,
        }}
        
        handler = handlers.get(action, self._handle_default)
        return handler(data, options)
    
    def _handle_default(self, data: Dict, options: Dict) -> Dict:
        """Default handler"""
        return {{
            "processed": True,
            "input_size": len(str(data)),
            "driver": self.driver
        }}
    
    def _handle_process(self, data: Dict, options: Dict) -> Dict:
        """Process data"""
        items = data.get("items", [data])
        processed = []
        
        for item in items if isinstance(items, list) else [items]:
            processed.append({{
                "original": item,
                "processed": True,
                "checksum": self._generate_id(item)[:8]
            }})
        
        return {{"items": processed, "count": len(processed)}}
    
    def _handle_transform(self, data: Dict, options: Dict) -> Dict:
        """Transform data"""
        format_type = options.get("format", "json")
        return {{
            "transformed": True,
            "format": format_type,
            "data": data,
            "size": len(str(data))
        }}
    
    def _handle_validate(self, data: Dict, options: Dict) -> Dict:
        """Validate data"""
        rules = options.get("rules", [])
        return {{
            "valid": True,
            "rules_checked": len(rules),
            "passed": len(rules),
            "failed": 0
        }}
    
    def _handle_query(self, data: Dict, options: Dict) -> Dict:
        """Query operation"""
        query = data.get("query", "")
        return {{
            "query": query,
            "results": [],
            "count": 0,
            "executed": True
        }}
    
    def _generate_id(self, data: Any) -> str:
        """Generate unique ID from data"""
        content = str(data) + str(time.time())
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get_metrics(self) -> Dict:
        """Return execution metrics"""
        return self.metrics


def execute(payload: Dict = None) -> Dict:
    """Module entry point for execution"""
    instance = {class_name}Execute()
    return instance.execute(payload)
'''
    
    @staticmethod
    def get_cleanup_template(category: str, module_id: str, driver: str) -> str:
        class_name = f"{category.title()}_{module_id}"
        
        return f'''"""
Aurora Module: {category}_{module_id}
Category: {category}
Driver: {driver}
Type: cleanup
Generated: {datetime.now(timezone.utc).isoformat()}
"""


class {class_name}Cleanup:
    """Cleanup {category} module resources"""
    
    def __init__(self, ctx=None):
        self.ctx = ctx or {{}}
        self.driver = "{driver}"
        self.resources_freed = []
    
    def cleanup(self) -> dict:
        """Main cleanup entry point"""
        try:
            self._cleanup_buffers()
            self._cleanup_connections()
            self._cleanup_state()
            
            return {{
                "status": "cleaned",
                "resources_freed": self.resources_freed,
                "driver": self.driver
            }}
        except Exception as e:
            return {{
                "status": "error",
                "error": str(e),
                "partial_cleanup": self.resources_freed
            }}
    
    def _cleanup_buffers(self):
        """Clear any buffers"""
        buffer = self.ctx.get("buffer", [])
        if buffer:
            buffer.clear()
            self.resources_freed.append("buffer")
    
    def _cleanup_connections(self):
        """Close any connections"""
        connections = self.ctx.get("connections", [])
        for conn in connections:
            if hasattr(conn, "close"):
                conn.close()
        self.resources_freed.append("connections")
    
    def _cleanup_state(self):
        """Reset state"""
        self.ctx.clear()
        self.resources_freed.append("state")


def cleanup(ctx=None) -> dict:
    """Module entry point for cleanup"""
    instance = {class_name}Cleanup(ctx)
    return instance.cleanup()
'''


class CandidateGenerator:
    """Generate candidate modules for testing"""
    
    def __init__(self, candidates_dir: str = None):
        self.candidates_dir = Path(candidates_dir) if candidates_dir else Path("candidates")
        self.candidates_dir.mkdir(parents=True, exist_ok=True)
        self.generated = []
    
    def generate(self, module_id: str, category: str, driver: str = "default") -> GenerationResult:
        """Generate a candidate module"""
        try:
            category_dir = self.candidates_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            files = []
            combined_content = ""
            
            templates = {
                "init": CodeTemplates.get_init_template(category, module_id, driver),
                "execute": CodeTemplates.get_execute_template(category, module_id, driver),
                "cleanup": CodeTemplates.get_cleanup_template(category, module_id, driver),
            }
            
            for phase, content in templates.items():
                filename = f"{category}_{module_id}_{phase}.py"
                filepath = category_dir / filename
                
                with open(filepath, 'w') as f:
                    f.write(content)
                
                files.append(str(filepath))
                combined_content += content
            
            checksum = hashlib.sha256(combined_content.encode()).hexdigest()[:16]
            
            result = GenerationResult(
                module_id=module_id,
                category=category,
                driver=driver,
                files=files,
                success=True,
                checksum=checksum
            )
            
            self.generated.append(result)
            return result
            
        except Exception as e:
            return GenerationResult(
                module_id=module_id,
                category=category,
                driver=driver,
                success=False,
                error=str(e)
            )
    
    def generate_batch(self, modules: List[Dict]) -> List[GenerationResult]:
        """Generate multiple candidate modules"""
        results = []
        
        for module in modules:
            result = self.generate(
                module_id=module["id"],
                category=module["category"],
                driver=module.get("driver", "default")
            )
            results.append(result)
        
        return results
    
    def get_candidate_path(self, module_id: str, category: str, phase: str) -> Path:
        """Get path to candidate file"""
        return self.candidates_dir / category / f"{category}_{module_id}_{phase}.py"
    
    def candidate_exists(self, module_id: str, category: str) -> bool:
        """Check if candidate exists"""
        execute_path = self.get_candidate_path(module_id, category, "execute")
        return execute_path.exists()
    
    def delete_candidate(self, module_id: str, category: str) -> bool:
        """Delete a candidate module"""
        try:
            for phase in ["init", "execute", "cleanup"]:
                path = self.get_candidate_path(module_id, category, phase)
                if path.exists():
                    path.unlink()
            return True
        except Exception:
            return False


class SnapshotManager:
    """Manage module snapshots for rollback"""
    
    def __init__(self, snapshots_dir: str = None, max_versions: int = 5):
        self.snapshots_dir = Path(snapshots_dir) if snapshots_dir else Path("snapshots")
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.max_versions = max_versions
        self.registry = {}
        self._load_registry()
    
    def _load_registry(self):
        """Load snapshot registry from disk"""
        registry_path = self.snapshots_dir / "registry.json"
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    self.registry = json.load(f)
            except json.JSONDecodeError:
                self.registry = {}
    
    def _save_registry(self):
        """Save snapshot registry to disk"""
        registry_path = self.snapshots_dir / "registry.json"
        with open(registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def create_snapshot(self, module_path: str, module_id: str) -> Optional[SnapshotInfo]:
        """Create a snapshot of a module file"""
        path = Path(module_path)
        
        if not path.exists():
            return None
        
        try:
            module_snapshot_dir = self.snapshots_dir / module_id
            module_snapshot_dir.mkdir(parents=True, exist_ok=True)
            
            if module_id not in self.registry:
                self.registry[module_id] = {"versions": [], "current": 0}
            
            version = self.registry[module_id]["current"] + 1
            
            with open(path, 'r') as f:
                content = f.read()
            
            checksum = hashlib.sha256(content.encode()).hexdigest()[:16]
            
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            snapshot_name = f"{path.stem}.v{version}.{timestamp}.snapshot"
            snapshot_path = module_snapshot_dir / snapshot_name
            
            shutil.copy2(path, snapshot_path)
            
            snapshot_info = SnapshotInfo(
                module_id=module_id,
                snapshot_path=str(snapshot_path),
                original_path=str(path),
                version=version,
                checksum=checksum,
                created=datetime.now(timezone.utc).isoformat()
            )
            
            self.registry[module_id]["versions"].append(asdict(snapshot_info))
            self.registry[module_id]["current"] = version
            
            self._cleanup_old_versions(module_id)
            
            self._save_registry()
            
            return snapshot_info
            
        except Exception as e:
            logger.error(f"Failed to create snapshot: {e}")
            return None
    
    def _cleanup_old_versions(self, module_id: str):
        """Remove old snapshots beyond max_versions"""
        if module_id not in self.registry:
            return
        
        versions = self.registry[module_id]["versions"]
        
        while len(versions) > self.max_versions:
            old = versions.pop(0)
            old_path = Path(old["snapshot_path"])
            if old_path.exists():
                old_path.unlink()
    
    def restore_snapshot(self, module_id: str, version: int = None) -> bool:
        """Restore a module from snapshot"""
        if module_id not in self.registry:
            return False
        
        versions = self.registry[module_id]["versions"]
        if not versions:
            return False
        
        if version is None:
            snapshot = versions[-1]
        else:
            snapshot = next((v for v in versions if v["version"] == version), None)
            if not snapshot:
                return False
        
        try:
            snapshot_path = Path(snapshot["snapshot_path"])
            original_path = Path(snapshot["original_path"])
            
            if not snapshot_path.exists():
                return False
            
            shutil.copy2(snapshot_path, original_path)
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore snapshot: {e}")
            return False
    
    def get_snapshots(self, module_id: str) -> List[Dict]:
        """Get all snapshots for a module"""
        if module_id not in self.registry:
            return []
        return self.registry[module_id]["versions"]
    
    def get_latest_snapshot(self, module_id: str) -> Optional[Dict]:
        """Get the latest snapshot for a module"""
        snapshots = self.get_snapshots(module_id)
        return snapshots[-1] if snapshots else None


class PromoteManager:
    """Manage promotion of candidates to production"""
    
    def __init__(self, candidates_dir: str = None, production_dir: str = None,
                 snapshots_dir: str = None):
        self.candidates_dir = Path(candidates_dir) if candidates_dir else Path("candidates")
        self.production_dir = Path(production_dir) if production_dir else Path("modules")
        self.snapshot_manager = SnapshotManager(snapshots_dir)
        self.production_dir.mkdir(parents=True, exist_ok=True)
        self.promotions = []
    
    def promote(self, module_id: str, category: str, 
                create_snapshot: bool = True) -> PromoteResult:
        """Promote a candidate module to production"""
        files_promoted = []
        snapshots_created = []
        
        try:
            candidate_dir = self.candidates_dir / category
            target_dir = self.production_dir / category
            target_dir.mkdir(parents=True, exist_ok=True)
            
            for phase in ["init", "execute", "cleanup"]:
                filename = f"{category}_{module_id}_{phase}.py"
                src = candidate_dir / filename
                dst = target_dir / filename
                
                if not src.exists():
                    return PromoteResult(
                        module_id=module_id,
                        category=category,
                        promoted=False,
                        error=f"Candidate file not found: {src}"
                    )
                
                if create_snapshot and dst.exists():
                    snapshot = self.snapshot_manager.create_snapshot(str(dst), module_id)
                    if snapshot:
                        snapshots_created.append(snapshot.snapshot_path)
                
                shutil.copy2(src, dst)
                files_promoted.append(str(dst))
            
            result = PromoteResult(
                module_id=module_id,
                category=category,
                promoted=True,
                files_promoted=files_promoted,
                snapshots_created=snapshots_created
            )
            
            self.promotions.append(result)
            return result
            
        except Exception as e:
            return PromoteResult(
                module_id=module_id,
                category=category,
                promoted=False,
                error=str(e)
            )
    
    def demote(self, module_id: str, category: str, version: int = None) -> bool:
        """Demote a production module (rollback to snapshot)"""
        return self.snapshot_manager.restore_snapshot(module_id, version)
    
    def promote_batch(self, modules: List[Dict], create_snapshots: bool = True) -> List[PromoteResult]:
        """Promote multiple modules"""
        results = []
        
        for module in modules:
            result = self.promote(
                module_id=module["id"],
                category=module["category"],
                create_snapshot=create_snapshots
            )
            results.append(result)
        
        return results
    
    def get_promotion_history(self) -> List[Dict]:
        """Get promotion history"""
        return [asdict(p) for p in self.promotions]
    
    def is_promoted(self, module_id: str, category: str) -> bool:
        """Check if a module is in production"""
        execute_path = self.production_dir / category / f"{category}_{module_id}_execute.py"
        return execute_path.exists()


def create_generator(candidates_dir: str = None) -> CandidateGenerator:
    return CandidateGenerator(candidates_dir)


def create_snapshot_manager(snapshots_dir: str = None, max_versions: int = 5) -> SnapshotManager:
    return SnapshotManager(snapshots_dir, max_versions)


def create_promote_manager(candidates_dir: str = None, production_dir: str = None,
                          snapshots_dir: str = None) -> PromoteManager:
    return PromoteManager(candidates_dir, production_dir, snapshots_dir)


if __name__ == "__main__":
    generator = CandidateGenerator("test_candidates")
    
    result = generator.generate("0001", "connector", "http")
    print(f"Generated: {result.success}, files: {result.files}")
    
    result = generator.generate("0002", "analyzer", "pattern")
    print(f"Generated: {result.success}, files: {result.files}")
    
    promote_mgr = PromoteManager(
        candidates_dir="test_candidates",
        production_dir="test_production",
        snapshots_dir="test_snapshots"
    )
    
    promote_result = promote_mgr.promote("0001", "connector")
    print(f"Promoted: {promote_result.promoted}")
    print(f"Files: {promote_result.files_promoted}")
    
    promote_result2 = promote_mgr.promote("0001", "connector")
    print(f"Re-promoted: {promote_result2.promoted}")
    print(f"Snapshots created: {promote_result2.snapshots_created}")
