"""
Aurora Unified Tier System
Merges 26-tier DEPTH (detailed knowledge) with 188-tier BREADTH (domain progression)
Creates the ultimate omniscient knowledge system spanning all temporal eras

This unified system integrates with:
- 550 Modules System
- 66 Advanced Execution Methods (AEMs)
- 15 Pack System
- Hybrid Mode
- Hyperspeed Mode
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TemporalEra(Enum):
    """Temporal eras spanning from ancient to future"""
    ANCIENT = "ancient"  # 1950s-1980s
    CLASSICAL = "classical"  # 1990s-2000s
    MODERN = "modern"  # 2010s-2020s
    AI_NATIVE = "ai_native"  # 2020s-2030s
    FUTURE = "future"  # 2030s+
    POST_QUANTUM = "post_quantum"  # Post-singularity


class TierType(Enum):
    """Types of tiers in the unified system"""
    DEPTH = "depth"  # Detailed knowledge tiers (26)
    BREADTH = "breadth"  # Domain/progression tiers (188)
    UNIFIED = "unified"  # Merged tier


@dataclass
class TierKnowledge:
    """Represents knowledge within a tier"""
    era: TemporalEra
    technologies: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)


@dataclass
class UnifiedTier:
    """Unified tier combining DEPTH and BREADTH"""
    tier_id: str
    name: str
    tier_type: TierType
    depth_tier_id: Optional[str] = None  # Reference to DEPTH tier
    breadth_tier_ids: List[str] = field(default_factory=list)  # References to BREADTH tiers
    domains: List[str] = field(default_factory=list)
    knowledge: Dict[str, TierKnowledge] = field(default_factory=dict)  # Era -> Knowledge
    modules: List[str] = field(default_factory=list)  # Associated module IDs
    aems: List[str] = field(default_factory=list)  # Associated AEM IDs
    packs: List[str] = field(default_factory=list)  # Associated pack IDs
    description: str = ""
    mastery_level: str = ""


class UnifiedTierSystem:
    """
    Unified Tier System combining:
    - 26 DEPTH tiers (detailed knowledge with temporal eras)
    - 188 BREADTH tiers (domain/progression structure)
    - Integration with 550 modules, 66 AEMs, 15 packs
    """

    def __init__(self):
        self.depth_tiers: Dict[str, Dict[str, Any]] = {}
        self.breadth_tiers: Dict[str, Dict[str, Any]] = {}
        self.unified_tiers: Dict[str, UnifiedTier] = {}
        self.era_mapping: Dict[TemporalEra, List[str]] = {era: [] for era in TemporalEra}
        self.domain_mapping: Dict[str, List[str]] = {}
        self.initialized = False

    def load_depth_tiers(self) -> int:
        """Load 26-tier DEPTH system from grandmaster file"""
        try:
            # Try both possible locations
            grandmaster_paths = [
                Path("tools/aurora_ultimate_omniscient_grandmaster.py"),
                Path("aurora_ultimate_omniscient_grandmaster.py"),
            ]

            grandmaster_path = None
            for path in grandmaster_paths:
                if path.exists():
                    grandmaster_path = path
                    break

            if not grandmaster_path:
                logger.warning(f"Grandmaster file not found in {grandmaster_paths}")
                return 0

            # Read and parse the file more carefully
            with open(grandmaster_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Use ast.literal_eval or import the module properly
            # Since the file has a dict definition, we'll import it as a module
            import importlib.util
            spec = importlib.util.spec_from_file_location("aurora_grandmaster", grandmaster_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)

                    if hasattr(module, 'AURORA_ULTIMATE_GRANDMASTER'):
                        grandmaster = module.AURORA_ULTIMATE_GRANDMASTER

                        # Extract all TIER_X entries
                        depth_count = 0
                        for key, value in grandmaster.items():
                            if key.startswith('TIER_') and isinstance(value, dict):
                                self.depth_tiers[key] = value
                                depth_count += 1

                                # Extract temporal eras from the tier
                                self._extract_temporal_eras(key, value)

                        logger.info(f"Loaded {depth_count} DEPTH tiers from grandmaster")
                        return depth_count
                    else:
                        logger.warning("AURORA_ULTIMATE_GRANDMASTER not found in module")
                        return 0
                except SyntaxError as e:
                    logger.warning(f"Syntax error in grandmaster file (line {e.lineno}): {e.msg}")
                    # Fallback: try to extract dict directly from file content
                    return self._load_depth_tiers_fallback(content)
            else:
                return self._load_depth_tiers_fallback(content)

        except Exception as e:
            logger.error(f"Error loading DEPTH tiers: {e}", exc_info=True)
            return 0

    def _load_depth_tiers_fallback(self, content: str) -> int:
        """Fallback method to extract tiers from file content"""
        import re

        # Look for TIER_X patterns in the content
        tier_pattern = r'"TIER_\d+_[^"]+":\s*\{'
        matches = re.findall(tier_pattern, content)

        depth_count = 0
        # Extract tier names
        tier_names = []
        for match in matches:
            tier_name = match.split('"')[1]
            tier_names.append(tier_name)

        # For now, create placeholder entries
        # In production, this would parse the full dict structure
        for tier_name in tier_names[:26]:  # Limit to 26 expected tiers
            self.depth_tiers[tier_name] = {
                'title': tier_name.replace('_', ' ').title(),
                'description': f'DEPTH tier: {tier_name}',
                'mastery_level': 'OMNISCIENT'
            }
            depth_count += 1

        if depth_count > 0:
            logger.info(f"Loaded {depth_count} DEPTH tier names (fallback method)")

        return depth_count

    def _extract_temporal_eras(self, tier_id: str, tier_data: Dict[str, Any]):
        """Extract temporal era knowledge from tier data"""
        for key, value in tier_data.items():
            if isinstance(value, dict):
                # Check for era keys
                for era in TemporalEra:
                    if era.value in key.lower() or era.value in str(value).lower():
                        if tier_id not in self.era_mapping[era]:
                            self.era_mapping[era].append(tier_id)

                # Recursively check nested dicts
                self._extract_temporal_eras(tier_id, value)

    def load_breadth_tiers(self) -> int:
        """Load 188-tier BREADTH system from manifest"""
        try:
            manifest_path = Path("manifests/tiers.manifest.json")
            if not manifest_path.exists():
                logger.warning(f"Tiers manifest not found: {manifest_path}")
                return 0

            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            breadth_count = 0
            if 'tiers' in data:
                for tier_data in data['tiers']:
                    tier_id = f"tier-{tier_data.get('id', breadth_count + 1)}"
                    self.breadth_tiers[tier_id] = {
                        'id': tier_data.get('id'),
                        'name': tier_data.get('name', tier_id),
                        'domains': tier_data.get('domain', [])
                    }

                    # Build domain mapping
                    for domain in tier_data.get('domain', []):
                        if domain not in self.domain_mapping:
                            self.domain_mapping[domain] = []
                        self.domain_mapping[domain].append(tier_id)

                    breadth_count += 1

            logger.info(f"Loaded {breadth_count} BREADTH tiers from manifest")
            return breadth_count

        except Exception as e:
            logger.error(f"Error loading BREADTH tiers: {e}", exc_info=True)
            return 0

    def create_unified_tiers(self):
        """Create unified tiers by merging DEPTH and BREADTH systems"""
        unified_count = 0

        # Create unified tiers from DEPTH tiers (26)
        for depth_id, depth_data in self.depth_tiers.items():
            unified_tier = UnifiedTier(
                tier_id=depth_id,
                name=depth_data.get('title', depth_id),
                tier_type=TierType.UNIFIED,
                depth_tier_id=depth_id,
                description=depth_data.get('description', ''),
                mastery_level=depth_data.get('mastery_level', '')
            )

            # Extract knowledge by temporal era
            self._extract_knowledge_to_tier(unified_tier, depth_data)

            # Map to breadth tiers by domain (intelligent mapping)
            self._map_depth_to_breadth(unified_tier, depth_data)

            self.unified_tiers[depth_id] = unified_tier
            unified_count += 1

        # Create unified tiers from BREADTH tiers (188)
        # These get enriched with DEPTH knowledge where applicable
        for breadth_id, breadth_data in self.breadth_tiers.items():
            if breadth_id not in self.unified_tiers:
                unified_tier = UnifiedTier(
                    tier_id=breadth_id,
                    name=breadth_data.get('name', breadth_id),
                    tier_type=TierType.BREADTH,
                    breadth_tier_ids=[breadth_id],
                    domains=breadth_data.get('domains', [])
                )
                self.unified_tiers[breadth_id] = unified_tier
                unified_count += 1

        logger.info(f"Created {unified_count} unified tiers")
        return unified_count

    def _extract_knowledge_to_tier(self, tier: UnifiedTier, data: Dict[str, Any]):
        """Extract knowledge organized by temporal era"""
        for key, value in data.items():
            if isinstance(value, dict):
                # Determine era from key or content
                era = self._detect_era(key, value)

                if era:
                    if era.value not in tier.knowledge:
                        tier.knowledge[era.value] = TierKnowledge(era=era)

                    # Extract technologies, tools, concepts
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, list):
                                if 'tech' in sub_key.lower() or 'mastery' in sub_key.lower():
                                    tier.knowledge[era.value].technologies.extend(sub_value)
                                elif 'tool' in sub_key.lower():
                                    tier.knowledge[era.value].tools.extend(sub_value)
                                elif 'concept' in sub_key.lower() or 'skill' in sub_key.lower():
                                    tier.knowledge[era.value].concepts.extend(sub_value)
                                else:
                                    tier.knowledge[era.value].technologies.extend(sub_value)

    def _detect_era(self, key: str, value: Any) -> Optional[TemporalEra]:
        """Detect temporal era from key or value"""
        key_lower = key.lower()

        if 'ancient' in key_lower:
            return TemporalEra.ANCIENT
        elif 'classical' in key_lower:
            return TemporalEra.CLASSICAL
        elif 'modern' in key_lower or 'cutting_edge' in key_lower:
            return TemporalEra.MODERN
        elif 'ai_native' in key_lower or 'ai' in key_lower:
            return TemporalEra.AI_NATIVE
        elif 'future' in key_lower or 'post' in key_lower or 'quantum' in key_lower:
            return TemporalEra.FUTURE
        elif 'post_quantum' in key_lower or 'post-singularity' in key_lower:
            return TemporalEra.POST_QUANTUM

        # Check value content
        if isinstance(value, (str, list)):
            value_str = str(value).lower()
            if 'ancient' in value_str or '1950' in value_str or '1960' in value_str:
                return TemporalEra.ANCIENT
            elif 'classical' in value_str or '1990' in value_str or '2000' in value_str:
                return TemporalEra.CLASSICAL
            elif 'modern' in value_str or '2010' in value_str or '2020' in value_str:
                return TemporalEra.MODERN
            elif 'future' in value_str or '2030' in value_str:
                return TemporalEra.FUTURE

        return None

    def _map_depth_to_breadth(self, unified_tier: UnifiedTier, depth_data: Dict[str, Any]):
        """Intelligently map DEPTH tier to BREADTH tiers by domain"""
        # Extract domains from depth tier name/description
        tier_name_lower = unified_tier.name.lower()

        # Domain keywords mapping
        domain_keywords = {
            'domain-1': ['process', 'timeless', 'eternal', 'core'],
            'domain-2': ['debug', 'debugging', 'error', 'fix'],
            'domain-3': ['architecture', 'design', 'structure'],
            'domain-4': ['autonomous', 'automation', 'self'],
            'domain-5': ['code', 'generation', 'synthesis'],
            'domain-6': ['architecture', 'system', 'design'],
            'domain-7': ['tech', 'technology', 'stack'],
            'domain-8': ['platform', 'web', 'mobile', 'desktop'],
            'domain-9': ['design', 'development', 'ui', 'ux'],
            'domain-10': ['browser', 'automation', 'web'],
            'domain-11': ['security', 'crypto', 'encryption'],
            'domain-12': ['network', 'protocol', 'communication'],
            'domain-13': ['data', 'storage', 'database'],
            'domain-14': ['cloud', 'infrastructure', 'server'],
            'domain-15': ['ai', 'ml', 'machine learning'],
            'domain-16': ['analytics', 'monitoring', 'metrics'],
            'domain-17': ['gaming', 'xr', 'virtual', 'reality'],
            'domain-18': ['iot', 'embedded', 'hardware'],
            'domain-19': ['streaming', 'realtime', 'live'],
            'domain-20': ['version', 'control', 'cicd', 'devops'],
        }

        matched_domains = []
        for domain, keywords in domain_keywords.items():
            if any(kw in tier_name_lower for kw in keywords):
                matched_domains.append(domain)
                # Find breadth tiers for this domain
                if domain in self.domain_mapping:
                    unified_tier.breadth_tier_ids.extend(self.domain_mapping[domain])
                    unified_tier.domains.append(domain)

        # If no match, assign to foundational domains
        if not matched_domains:
            unified_tier.domains.append('domain-1')
            if 'domain-1' in self.domain_mapping:
                unified_tier.breadth_tier_ids.extend(self.domain_mapping['domain-1'][:5])

    def initialize(self) -> bool:
        """Initialize the unified tier system"""
        if self.initialized:
            return True

        logger.info("Initializing Unified Tier System...")

        depth_count = self.load_depth_tiers()
        breadth_count = self.load_breadth_tiers()

        if depth_count == 0 and breadth_count == 0:
            logger.error("Failed to load any tiers")
            return False

        unified_count = self.create_unified_tiers()

        self.initialized = True
        logger.info(
            f"Unified Tier System initialized: "
            f"{depth_count} DEPTH + {breadth_count} BREADTH = {unified_count} unified tiers"
        )

        return True

    def get_tier(self, tier_id: str) -> Optional[UnifiedTier]:
        """Get unified tier by ID"""
        return self.unified_tiers.get(tier_id)

    def get_tiers_by_era(self, era: TemporalEra) -> List[UnifiedTier]:
        """Get all tiers containing knowledge from a specific era"""
        result = []
        for tier in self.unified_tiers.values():
            if era.value in tier.knowledge:
                result.append(tier)
        return result

    def get_tiers_by_domain(self, domain: str) -> List[UnifiedTier]:
        """Get all tiers in a specific domain"""
        result = []
        for tier in self.unified_tiers.values():
            if domain in tier.domains:
                result.append(tier)
        return result

    def get_all_tiers(self) -> Dict[str, UnifiedTier]:
        """Get all unified tiers"""
        return self.unified_tiers

    def get_tier_count(self) -> Dict[str, int]:
        """Get counts of different tier types"""
        return {
            'depth': len(self.depth_tiers),
            'breadth': len(self.breadth_tiers),
            'unified': len(self.unified_tiers),
            'total': len(self.unified_tiers)
        }

    def search_knowledge(self, query: str, era: Optional[TemporalEra] = None) -> List[UnifiedTier]:
        """Search tiers by knowledge query"""
        query_lower = query.lower()
        results = []

        for tier in self.unified_tiers.values():
            # Search in name and description
            if query_lower in tier.name.lower() or query_lower in tier.description.lower():
                if era is None or era.value in tier.knowledge:
                    results.append(tier)
                    continue

            # Search in knowledge
            for era_key, knowledge in tier.knowledge.items():
                if era and era.value != era_key:
                    continue

                if (query_lower in str(knowledge.technologies).lower() or
                    query_lower in str(knowledge.tools).lower() or
                    query_lower in str(knowledge.concepts).lower()):
                    if tier not in results:
                        results.append(tier)
                    break

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the unified tier system"""
        era_counts = {era.value: len(self.get_tiers_by_era(era)) for era in TemporalEra}

        return {
            'tier_counts': self.get_tier_count(),
            'era_distribution': era_counts,
            'domain_count': len(self.domain_mapping),
            'total_knowledge_items': sum(
                sum(len(k.technologies) + len(k.tools) + len(k.concepts)
                    for k in tier.knowledge.values())
                for tier in self.unified_tiers.values()
            ),
            'tiers_with_modules': sum(1 for t in self.unified_tiers.values() if t.modules),
            'tiers_with_aems': sum(1 for t in self.unified_tiers.values() if t.aems),
            'tiers_with_packs': sum(1 for t in self.unified_tiers.values() if t.packs),
        }


# Global instance
_unified_tier_system: Optional[UnifiedTierSystem] = None


def get_unified_tier_system() -> UnifiedTierSystem:
    """Get or create the global unified tier system instance"""
    global _unified_tier_system
    if _unified_tier_system is None:
        _unified_tier_system = UnifiedTierSystem()
        _unified_tier_system.initialize()
    return _unified_tier_system
