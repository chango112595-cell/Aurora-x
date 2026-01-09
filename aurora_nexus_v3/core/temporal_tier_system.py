"""
Aurora Temporal Tier System
Adds temporal era coverage to all modules: Ancient, Classical, Modern, Future, Post-Quantum

Currently modules only have 'foundational' tier - this system adds full temporal coverage
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum
import json

logger = logging.getLogger(__name__)


class TemporalEra(Enum):
    """Temporal eras for module classification"""
    ANCIENT = "ancient"  # 1950s-1980s - Foundational computing
    CLASSICAL = "classical"  # 1990s-2000s - Modern computing foundations
    MODERN = "modern"  # 2010s-2020s - Current technologies
    FUTURE = "future"  # 2030s+ - Emerging paradigms
    POST_QUANTUM = "post_quantum"  # Post-singularity computing
    FOUNDATIONAL = "foundational"  # Current default


class TemporalTierSystem:
    """
    Temporal Tier System
    Adds temporal era coverage to all 550 modules
    """
    
    def __init__(self):
        self.temporal_mappings: Dict[int, List[TemporalEra]] = {}
        self.module_temporal_data: Dict[int, Dict[str, Any]] = {}
        self.initialized = False
    
    def initialize(self):
        """Initialize temporal tier system"""
        if self.initialized:
            return
        
        # Generate temporal mappings for all 550 modules
        self._generate_temporal_mappings()
        
        self.initialized = True
        logger.info(f"Temporal Tier System initialized for 550 modules")
    
    def _generate_temporal_mappings(self):
        """Generate temporal era mappings for all modules"""
        # Distribute modules across temporal eras
        # Each module can belong to multiple eras
        
        for module_id in range(1, 551):
            eras = []
            
            # Assign eras based on module ID patterns
            # This creates a distribution across all eras
            
            # Ancient era (modules 1-110)
            if module_id <= 110:
                eras.append(TemporalEra.ANCIENT)
            
            # Classical era (modules 111-220)
            if 111 <= module_id <= 220:
                eras.append(TemporalEra.CLASSICAL)
            
            # Modern era (modules 221-330)
            if 221 <= module_id <= 330:
                eras.append(TemporalEra.MODERN)
            
            # Future era (modules 331-440)
            if 331 <= module_id <= 440:
                eras.append(TemporalEra.FUTURE)
            
            # Post-Quantum era (modules 441-550)
            if 441 <= module_id <= 550:
                eras.append(TemporalEra.POST_QUANTUM)
            
            # All modules also have foundational
            eras.append(TemporalEra.FOUNDATIONAL)
            
            # Ensure some modules span multiple eras (cross-temporal)
            if module_id % 10 == 0:
                # Every 10th module spans multiple eras
                if TemporalEra.ANCIENT not in eras:
                    eras.append(TemporalEra.ANCIENT)
                if TemporalEra.MODERN not in eras:
                    eras.append(TemporalEra.MODERN)
            
            self.temporal_mappings[module_id] = eras
            
            # Create temporal metadata
            self.module_temporal_data[module_id] = {
                "module_id": module_id,
                "primary_era": eras[0].value if eras else TemporalEra.FOUNDATIONAL.value,
                "eras": [e.value for e in eras],
                "era_count": len(eras),
                "cross_temporal": len(eras) > 1,
            }
    
    def get_module_eras(self, module_id: int) -> List[TemporalEra]:
        """Get temporal eras for a module"""
        return self.temporal_mappings.get(module_id, [TemporalEra.FOUNDATIONAL])
    
    def get_modules_by_era(self, era: TemporalEra) -> List[int]:
        """Get all modules in a specific temporal era"""
        return [
            module_id for module_id, eras in self.temporal_mappings.items()
            if era in eras
        ]
    
    def get_temporal_coverage(self) -> Dict[str, int]:
        """Get coverage statistics by era"""
        coverage = {}
        for era in TemporalEra:
            coverage[era.value] = len(self.get_modules_by_era(era))
        return coverage
    
    def get_module_temporal_info(self, module_id: int) -> Dict[str, Any]:
        """Get temporal information for a module"""
        return self.module_temporal_data.get(module_id, {
            "module_id": module_id,
            "primary_era": TemporalEra.FOUNDATIONAL.value,
            "eras": [TemporalEra.FOUNDATIONAL.value],
            "era_count": 1,
            "cross_temporal": False,
        })
    
    def update_module_temporal_tier(self, module_id: int, tier: str):
        """Update module's temporal tier (for compatibility)"""
        # Map tier string to era
        tier_lower = tier.lower()
        if "ancient" in tier_lower:
            era = TemporalEra.ANCIENT
        elif "classical" in tier_lower:
            era = TemporalEra.CLASSICAL
        elif "modern" in tier_lower:
            era = TemporalEra.MODERN
        elif "future" in tier_lower or "futuristic" in tier_lower:
            era = TemporalEra.FUTURE
        elif "post" in tier_lower or "quantum" in tier_lower:
            era = TemporalEra.POST_QUANTUM
        else:
            era = TemporalEra.FOUNDATIONAL
        
        # Add era to module if not present
        if module_id not in self.temporal_mappings:
            self.temporal_mappings[module_id] = []
        if era not in self.temporal_mappings[module_id]:
            self.temporal_mappings[module_id].append(era)
            self.module_temporal_data[module_id] = {
                "module_id": module_id,
                "primary_era": era.value,
                "eras": [e.value for e in self.temporal_mappings[module_id]],
                "era_count": len(self.temporal_mappings[module_id]),
                "cross_temporal": len(self.temporal_mappings[module_id]) > 1,
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get temporal tier system statistics"""
        coverage = self.get_temporal_coverage()
        cross_temporal_count = sum(
            1 for data in self.module_temporal_data.values()
            if data.get("cross_temporal", False)
        )
        
        return {
            "total_modules": len(self.temporal_mappings),
            "coverage_by_era": coverage,
            "cross_temporal_modules": cross_temporal_count,
            "modules_with_multiple_eras": cross_temporal_count,
        }


# Global instance
_temporal_tier_system: Optional[TemporalTierSystem] = None


def get_temporal_tier_system() -> TemporalTierSystem:
    """Get or create the global temporal tier system instance"""
    global _temporal_tier_system
    if _temporal_tier_system is None:
        _temporal_tier_system = TemporalTierSystem()
        _temporal_tier_system.initialize()
    return _temporal_tier_system
