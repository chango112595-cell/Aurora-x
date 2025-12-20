"""
Aurora Manifest Integrator - Connects 188 Tiers, 66 AEMs, 550 Modules
The bridge between manifest specifications and runtime execution

This module loads and integrates:
- 188 Grandmaster Tiers (knowledge strata)
- 66 Advanced Execution Methods (operational verbs)
- 550 Cross-Temporal Modules (tools spanning all eras)
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from aurora_nexus_v3.utils.atomic_io import load_snapshot


@dataclass
class Tier:
    id: str
    name: str
    domain: List[str]
    description: str
    capabilities: List[str]
    dependencies: List[str]
    version: str
    status: str
    priority: int


@dataclass
class ExecutionMethod:
    id: str
    name: str
    category: str
    inputs: List[str]
    outputs: List[str]
    safety_policy: List[str]
    strategy: str
    implementation_ref: str
    version: str
    status: str
    timeout_ms: int
    retry_policy: Dict[str, Any]


@dataclass
class Module:
    id: str
    name: str
    category: str
    supported_devices: List[str]
    entrypoints: Dict[str, str]
    sandbox: str
    permissions: List[str]
    version: str
    status: str
    dependencies: List[str]
    metadata: Dict[str, Any]


class ManifestIntegrator:
    """
    Integrates all Aurora manifests with the Nexus V3 core
    
    Provides:
    - Tier lookup and activation
    - AEM routing and execution
    - Module loading and orchestration
    - Cross-system coordination
    """
    
    MANIFEST_DIR = Path("manifests")
    
    def __init__(self, core: Any = None):
        self.core = core
        self.tiers: Dict[str, Tier] = {}
        self.execution_methods: Dict[str, ExecutionMethod] = {}
        self.modules: Dict[str, Module] = {}
        
        self.loaded = False
        self.load_time: Optional[datetime] = None
        
        self.tier_count = 0
        self.aem_count = 0
        self.module_count = 0
    
    async def initialize(self):
        """Initialize and load all manifests"""
        await self.load_manifests()
        self.loaded = True
        self.load_time = datetime.now()
        
        print(f"[AURORA MANIFEST] Loaded {self.tier_count} tiers, {self.aem_count} AEMs, {self.module_count} modules")
    
    async def load_manifests(self):
        """Load all manifest files"""
        await self._load_tiers()
        await self._load_execution_methods()
        await self._load_modules()
    
    async def _load_tiers(self):
        """Load 188 tiers from manifest"""
        tier_file = self.MANIFEST_DIR / "tiers.manifest.json"
        
        if not tier_file.exists():
            print(f"[AURORA MANIFEST] Warning: {tier_file} not found")
            return
        
        try:
            data = load_snapshot(str(tier_file), {"tiers": []})
            
            for tier_data in data.get("tiers", []):
                tier = Tier(
                    id=tier_data.get("id", ""),
                    name=tier_data.get("name", ""),
                    domain=tier_data.get("domain", []),
                    description=tier_data.get("description", ""),
                    capabilities=tier_data.get("capabilities", []),
                    dependencies=tier_data.get("dependencies", []),
                    version=tier_data.get("version", "0.0.0"),
                    status=tier_data.get("status", "placeholder"),
                    priority=tier_data.get("priority", 0)
                )
                self.tiers[tier.id] = tier
            
            self.tier_count = len(self.tiers)
            print(f"[AURORA MANIFEST] Loaded {self.tier_count} tiers")
            
        except Exception as e:
            print(f"[AURORA MANIFEST] Error loading tiers: {e}")
    
    async def _load_execution_methods(self):
        """Load 66 execution methods from manifest"""
        aem_file = self.MANIFEST_DIR / "executions.manifest.json"
        
        if not aem_file.exists():
            print(f"[AURORA MANIFEST] Warning: {aem_file} not found")
            return
        
        try:
            data = load_snapshot(str(aem_file), {"executions": []})
            
            for aem_data in data.get("executions", []):
                aem = ExecutionMethod(
                    id=aem_data.get("id", ""),
                    name=aem_data.get("name", ""),
                    category=aem_data.get("category", ""),
                    inputs=aem_data.get("inputs", []),
                    outputs=aem_data.get("outputs", []),
                    safety_policy=aem_data.get("safetyPolicy", []),
                    strategy=aem_data.get("strategy", "deterministic"),
                    implementation_ref=aem_data.get("implementationRef", ""),
                    version=aem_data.get("version", "0.0.0"),
                    status=aem_data.get("status", "placeholder"),
                    timeout_ms=aem_data.get("timeout_ms", 30000),
                    retry_policy=aem_data.get("retryPolicy", {})
                )
                self.execution_methods[aem.id] = aem
            
            self.aem_count = len(self.execution_methods)
            print(f"[AURORA MANIFEST] Loaded {self.aem_count} execution methods")
            
        except Exception as e:
            print(f"[AURORA MANIFEST] Error loading execution methods: {e}")
    
    async def _load_modules(self):
        """Load 550 modules from manifest"""
        module_file = self.MANIFEST_DIR / "modules.manifest.json"
        
        if not module_file.exists():
            print(f"[AURORA MANIFEST] Warning: {module_file} not found")
            return
        
        try:
            data = load_snapshot(str(module_file), {"modules": []})
            
            for mod_data in data.get("modules", []):
                module = Module(
                    id=mod_data.get("id", ""),
                    name=mod_data.get("name", ""),
                    category=mod_data.get("category", ""),
                    supported_devices=mod_data.get("supportedDevices", []),
                    entrypoints=mod_data.get("entrypoints", {}),
                    sandbox=mod_data.get("sandbox", "vm"),
                    permissions=mod_data.get("permissions", []),
                    version=mod_data.get("version", "0.0.0"),
                    status=mod_data.get("status", "placeholder"),
                    dependencies=mod_data.get("dependencies", []),
                    metadata=mod_data.get("metadata", {})
                )
                self.modules[module.id] = module
            
            self.module_count = len(self.modules)
            print(f"[AURORA MANIFEST] Loaded {self.module_count} modules")
            
        except Exception as e:
            print(f"[AURORA MANIFEST] Error loading modules: {e}")
    
    def get_tier(self, tier_id: str) -> Optional[Tier]:
        """Get a specific tier by ID"""
        return self.tiers.get(tier_id)
    
    def get_execution_method(self, aem_id: str) -> Optional[ExecutionMethod]:
        """Get a specific execution method by ID"""
        return self.execution_methods.get(aem_id)
    
    def get_module(self, module_id: str) -> Optional[Module]:
        """Get a specific module by ID"""
        return self.modules.get(module_id)
    
    def get_tiers_by_domain(self, domain: str) -> List[Tier]:
        """Get all tiers in a specific domain"""
        return [t for t in self.tiers.values() if domain in t.domain]
    
    def get_aems_by_category(self, category: str) -> List[ExecutionMethod]:
        """Get all AEMs in a specific category"""
        return [a for a in self.execution_methods.values() if a.category == category]
    
    def get_modules_by_category(self, category: str) -> List[Module]:
        """Get all modules in a specific category"""
        return [m for m in self.modules.values() if m.category == category]
    
    def get_active_tiers(self) -> List[Tier]:
        """Get all active (non-placeholder) tiers"""
        return [t for t in self.tiers.values() if t.status != "placeholder"]
    
    def get_active_aems(self) -> List[ExecutionMethod]:
        """Get all active (non-placeholder) execution methods"""
        return [a for a in self.execution_methods.values() if a.status != "placeholder"]
    
    def get_active_modules(self) -> List[Module]:
        """Get all active (non-placeholder) modules"""
        return [m for m in self.modules.values() if m.status != "placeholder"]
    
    def get_tier_dependencies(self, tier_id: str) -> List[Tier]:
        """Get all dependencies for a tier"""
        tier = self.get_tier(tier_id)
        if not tier:
            return []
        return [self.tiers[dep] for dep in tier.dependencies if dep in self.tiers]
    
    def get_module_dependencies(self, module_id: str) -> List[Module]:
        """Get all dependencies for a module"""
        module = self.get_module(module_id)
        if not module:
            return []
        return [self.modules[dep] for dep in module.dependencies if dep in self.modules]
    
    def get_tier_categories(self) -> Dict[str, int]:
        """Get tier count by domain"""
        categories: Dict[str, int] = {}
        for tier in self.tiers.values():
            for domain in tier.domain:
                categories[domain] = categories.get(domain, 0) + 1
        return categories
    
    def get_aem_categories(self) -> Dict[str, int]:
        """Get AEM count by category"""
        categories: Dict[str, int] = {}
        for aem in self.execution_methods.values():
            categories[aem.category] = categories.get(aem.category, 0) + 1
        return categories
    
    def get_module_categories(self) -> Dict[str, int]:
        """Get module count by category"""
        categories: Dict[str, int] = {}
        for module in self.modules.values():
            categories[module.category] = categories.get(module.category, 0) + 1
        return categories
    
    def get_status(self) -> Dict[str, Any]:
        """Get integrator status"""
        return {
            "loaded": self.loaded,
            "load_time": self.load_time.isoformat() if self.load_time else None,
            "tier_count": self.tier_count,
            "aem_count": self.aem_count,
            "module_count": self.module_count,
            "active_tiers": len(self.get_active_tiers()),
            "active_aems": len(self.get_active_aems()),
            "active_modules": len(self.get_active_modules()),
            "tier_categories": self.get_tier_categories(),
            "aem_categories": self.get_aem_categories(),
            "module_categories": self.get_module_categories()
        }
    
    async def shutdown(self):
        """Cleanup"""
        self.tiers.clear()
        self.execution_methods.clear()
        self.modules.clear()
        self.loaded = False
