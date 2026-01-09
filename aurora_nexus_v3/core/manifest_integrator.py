"""
Aurora Manifest Integrator - Connects 188 Tiers, 66 AEMs, 550 Modules
The bridge between manifest specifications and runtime execution

This module loads and integrates:
- 188 Grandmaster Tiers (knowledge strata)
- 66 Advanced Execution Methods (operational verbs)
- 550 Cross-Temporal Modules (tools spanning all eras)
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from aurora_nexus_v3.utils.atomic_io import load_snapshot
from aurora_nexus_v3.core.unified_tier_system import (
    get_unified_tier_system,
    UnifiedTier,
    TemporalEra,
)
from aurora_nexus_v3.core.unified_tier_system_advanced import (
    get_advanced_tier_system,
    AdvancedTierSystem,
)
from aurora_nexus_v3.core.aem_execution_engine import get_aem_engine, AEMExecutionEngine
from aurora_nexus_v3.core.temporal_tier_system import (
    get_temporal_tier_system,
    TemporalTierSystem,
    TemporalEra,
)


@dataclass
class Tier:
    id: str
    name: str
    domain: list[str]
    description: str
    capabilities: list[str]
    dependencies: list[str]
    version: str
    status: str
    priority: int


@dataclass
class ExecutionMethod:
    id: str
    name: str
    category: str
    inputs: list[str]
    outputs: list[str]
    safety_policy: list[str]
    strategy: str
    implementation_ref: str
    version: str
    status: str
    timeout_ms: int
    retry_policy: dict[str, Any]


@dataclass
class Module:
    id: str
    name: str
    category: str
    supported_devices: list[str]
    entrypoints: dict[str, str]
    sandbox: str
    permissions: list[str]
    version: str
    status: str
    dependencies: list[str]
    metadata: dict[str, Any]


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
    TEMPORAL_ERAS = ("Ancient", "Classical", "Modern", "Futuristic", "Post-Quantum")
    TEMPORAL_ALIAS = {"Futuristic": "Post-Quantum"}

    def __init__(self, core: Any = None):
        self.core = core
        self.tiers: dict[str, Tier] = {}
        self.execution_methods: dict[str, ExecutionMethod] = {}
        self.modules: dict[str, Module] = {}
        
        # Unified Tier System integration
        self.unified_tier_system = None
        self.advanced_tier_system = None
        
        # AEM Execution Engine integration
        self.aem_engine = None
        
        # Temporal Tier System integration
        self.temporal_tier_system = None

        self.loaded = False
        self.load_time: datetime | None = None

        self.tier_count = 0
        self.aem_count = 0
        self.module_count = 0

    async def initialize(self):
        """Initialize and load all manifests"""
        await self.load_manifests()
        
        # Initialize advanced unified tier system
        try:
            self.advanced_tier_system = get_advanced_tier_system(self)
            if self.advanced_tier_system.initialized:
                stats = self.advanced_tier_system.get_statistics()
                print(
                    f"[AURORA ADVANCED TIERS] "
                    f"{stats['tier_counts']['unified']} unified tiers "
                    f"({stats['tier_counts']['depth']} DEPTH + {stats['tier_counts']['breadth']} BREADTH), "
                    f"{stats['tiers_with_modules']} with modules, "
                    f"{stats['tiers_with_aems']} with AEMs, "
                    f"{stats['tiers_with_packs']} with packs, "
                    f"{stats['total_relationships']} relationships"
                )
            # Also initialize basic system for compatibility
            self.unified_tier_system = get_unified_tier_system()
        except Exception as e:
            print(f"[AURORA UNIFIED TIERS] Warning: Could not initialize advanced tier system: {e}")
            try:
                self.unified_tier_system = get_unified_tier_system()
            except Exception as e2:
                print(f"[AURORA UNIFIED TIERS] Warning: Could not initialize basic tier system: {e2}")
        
        # Initialize AEM Execution Engine
        try:
            self.aem_engine = await get_aem_engine()
            if self.aem_engine.initialized:
                aem_stats = self.aem_engine.get_statistics()
                print(
                    f"[AURORA AEM ENGINE] "
                    f"{aem_stats['total_aems']} Advanced Execution Methods loaded and ready"
                )
        except Exception as e:
            print(f"[AURORA AEM ENGINE] Warning: Could not initialize AEM engine: {e}")
        
        # Initialize Temporal Tier System
        try:
            self.temporal_tier_system = get_temporal_tier_system()
            if self.temporal_tier_system.initialized:
                temporal_stats = self.temporal_tier_system.get_statistics()
                coverage = temporal_stats['coverage_by_era']
                print(
                    f"[AURORA TEMPORAL TIERS] "
                    f"Temporal coverage: Ancient={coverage.get('ancient', 0)}, "
                    f"Classical={coverage.get('classical', 0)}, "
                    f"Modern={coverage.get('modern', 0)}, "
                    f"Future={coverage.get('future', 0)}, "
                    f"Post-Quantum={coverage.get('post_quantum', 0)}, "
                    f"Cross-temporal={temporal_stats['cross_temporal_modules']}"
                )
        except Exception as e:
            print(f"[AURORA TEMPORAL TIERS] Warning: Could not initialize temporal tier system: {e}")
        
        self.loaded = True
        self.load_time = datetime.now()

        print(
            f"[AURORA MANIFEST] Loaded {self.tier_count} tiers, {self.aem_count} AEMs, {self.module_count} modules"
        )

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
                    priority=tier_data.get("priority", 0),
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
                    retry_policy=aem_data.get("retryPolicy", {}),
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
                category = mod_data.get("category", "")
                temporal_era = mod_data.get("temporalEra") or self.TEMPORAL_ALIAS.get(
                    category, category
                )
                if temporal_era not in self.TEMPORAL_ERAS:
                    temporal_era = "Unknown"
                module = Module(
                    id=mod_data.get("id", ""),
                    name=mod_data.get("name", ""),
                    category=category,
                    supported_devices=mod_data.get("supportedDevices", []),
                    entrypoints=mod_data.get("entrypoints", {}),
                    sandbox=mod_data.get("sandbox", "vm"),
                    permissions=mod_data.get("permissions", []),
                    version=mod_data.get("version", "0.0.0"),
                    status=mod_data.get("status", "placeholder"),
                    dependencies=mod_data.get("dependencies", []),
                    metadata={**mod_data.get("metadata", {}), "temporal_era": temporal_era},
                )
                self.modules[module.id] = module

            self.module_count = len(self.modules)
            print(f"[AURORA MANIFEST] Loaded {self.module_count} modules")

        except Exception as e:
            print(f"[AURORA MANIFEST] Error loading modules: {e}")

    def get_tier(self, tier_id: str) -> Tier | None:
        """Get a specific tier by ID"""
        return self.tiers.get(tier_id)

    def get_execution_method(self, aem_id: str) -> ExecutionMethod | None:
        """Get a specific execution method by ID"""
        return self.execution_methods.get(aem_id)

    def get_module(self, module_id: str) -> Module | None:
        """Get a specific module by ID"""
        return self.modules.get(module_id)

    def get_tiers_by_domain(self, domain: str) -> list[Tier]:
        """Get all tiers in a specific domain"""
        return [t for t in self.tiers.values() if domain in t.domain]
    
    def get_unified_tier(self, tier_id: str) -> UnifiedTier | None:
        """Get unified tier (combines DEPTH + BREADTH)"""
        if self.advanced_tier_system:
            return self.advanced_tier_system.get_tier(tier_id)
        elif self.unified_tier_system:
            return self.unified_tier_system.get_tier(tier_id)
        return None
    
    def get_unified_tiers_by_era(self, era: str) -> list[UnifiedTier]:
        """Get unified tiers for a specific temporal era"""
        if self.advanced_tier_system:
            try:
                temporal_era = TemporalEra(era.lower())
                return self.advanced_tier_system.get_tiers_by_era(temporal_era)
            except ValueError:
                return []
        elif self.unified_tier_system:
            try:
                temporal_era = TemporalEra(era.lower())
                return self.unified_tier_system.get_tiers_by_era(temporal_era)
            except ValueError:
                return []
        return []
    
    def search_unified_knowledge(
        self,
        query: str,
        era: str | None = None,
        domain: str | None = None,
        min_knowledge_items: int = 0,
        include_related: bool = False
    ) -> list[UnifiedTier]:
        """Search unified tier knowledge (advanced)"""
        if self.advanced_tier_system:
            temporal_era = None
            if era:
                try:
                    temporal_era = TemporalEra(era.lower())
                except ValueError:
                    pass
            return self.advanced_tier_system.search_knowledge_advanced(
                query, temporal_era, domain, min_knowledge_items, include_related
            )
        elif self.unified_tier_system:
            temporal_era = None
            if era:
                try:
                    temporal_era = TemporalEra(era.lower())
                except ValueError:
                    pass
            return self.unified_tier_system.search_knowledge(query, temporal_era)
        return []
    
    def link_module_to_tier(self, module_id: str, tier_id: str):
        """Link a module to a unified tier"""
        if self.unified_tier_system:
            tier = self.unified_tier_system.get_tier(tier_id)
            if tier and module_id not in tier.modules:
                tier.modules.append(module_id)
    
    def link_aem_to_tier(self, aem_id: str, tier_id: str):
        """Link an AEM to a unified tier"""
        if self.unified_tier_system:
            tier = self.unified_tier_system.get_tier(tier_id)
            if tier and aem_id not in tier.aems:
                tier.aems.append(aem_id)
    
    def get_unified_tier_statistics(self) -> dict[str, Any] | None:
        """Get statistics about the unified tier system"""
        if self.advanced_tier_system:
            return self.advanced_tier_system.get_statistics()
        elif self.unified_tier_system:
            return self.unified_tier_system.get_statistics()
        return None
    
    def get_tier_routing_suggestions(self, task_type: str, payload: dict[str, Any]) -> list[str]:
        """Get tier routing suggestions for a task"""
        if self.advanced_tier_system:
            return self.advanced_tier_system.get_tier_routing_suggestions(task_type, payload)
        return []

    def get_aems_by_category(self, category: str) -> list[ExecutionMethod]:
        """Get all AEMs in a specific category"""
        return [a for a in self.execution_methods.values() if a.category == category]

    def get_modules_by_category(self, category: str) -> list[Module]:
        """Get all modules in a specific category"""
        return [m for m in self.modules.values() if m.category == category]

    def get_active_tiers(self) -> list[Tier]:
        """Get all active (non-placeholder) tiers"""
        return [t for t in self.tiers.values() if t.status != "placeholder"]

    def get_active_aems(self) -> list[ExecutionMethod]:
        """Get all active (non-placeholder) execution methods"""
        return [a for a in self.execution_methods.values() if a.status != "placeholder"]

    def get_active_modules(self) -> list[Module]:
        """Get all active (non-placeholder) modules"""
        return [m for m in self.modules.values() if m.status != "placeholder"]

    def get_tier_dependencies(self, tier_id: str) -> list[Tier]:
        """Get all dependencies for a tier"""
        tier = self.get_tier(tier_id)
        if not tier:
            return []
        return [self.tiers[dep] for dep in tier.dependencies if dep in self.tiers]

    def get_module_dependencies(self, module_id: str) -> list[Module]:
        """Get all dependencies for a module"""
        module = self.get_module(module_id)
        if not module:
            return []
        return [self.modules[dep] for dep in module.dependencies if dep in self.modules]

    def get_tier_categories(self) -> dict[str, int]:
        """Get tier count by domain"""
        categories: dict[str, int] = {}
        for tier in self.tiers.values():
            for domain in tier.domain:
                categories[domain] = categories.get(domain, 0) + 1
        return categories

    def get_aem_categories(self) -> dict[str, int]:
        """Get AEM count by category"""
        categories: dict[str, int] = {}
        for aem in self.execution_methods.values():
            categories[aem.category] = categories.get(aem.category, 0) + 1
        return categories

    def get_module_categories(self) -> dict[str, int]:
        """Get module count by category"""
        categories: dict[str, int] = {}
        for module in self.modules.values():
            categories[module.category] = categories.get(module.category, 0) + 1
        return categories

    def get_temporal_coverage(self) -> dict[str, int]:
        """Get module count by temporal era."""
        coverage = {era: 0 for era in self.TEMPORAL_ERAS}
        for module in self.modules.values():
            era = module.metadata.get("temporal_era", "Unknown")
            if era in coverage:
                coverage[era] += 1
        return coverage

    def get_status(self) -> dict[str, Any]:
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
            "module_categories": self.get_module_categories(),
            "temporal_coverage": self.get_temporal_coverage(),
        }

    async def shutdown(self):
        """Cleanup"""
        self.tiers.clear()
        self.execution_methods.clear()
        self.modules.clear()
        self.loaded = False
