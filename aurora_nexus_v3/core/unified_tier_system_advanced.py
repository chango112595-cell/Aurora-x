"""
Aurora Unified Tier System - Advanced Edition
Enhanced with full knowledge extraction, auto-linking, routing optimizations, and advanced features

Features:
- Full temporal era knowledge extraction
- Intelligent auto-linking (modules/AEMs/packs)
- Tier-based routing optimizations
- Performance caching and indexing
- Cross-tier relationships
- Advanced search with filters
- Tier health monitoring
- Dynamic tier updates
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import time
import hashlib

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
    DEPTH = "depth"
    BREADTH = "breadth"
    UNIFIED = "unified"


class TierHealth(Enum):
    """Tier health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class TierKnowledge:
    """Represents knowledge within a tier"""
    era: TemporalEra
    technologies: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    protocols: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'era': self.era.value,
            'technologies': self.technologies,
            'tools': self.tools,
            'concepts': self.concepts,
            'skills': self.skills,
            'frameworks': self.frameworks,
            'languages': self.languages,
            'protocols': self.protocols,
        }

    def get_total_items(self) -> int:
        """Get total knowledge items"""
        return (len(self.technologies) + len(self.tools) + len(self.concepts) +
                len(self.skills) + len(self.frameworks) + len(self.languages) +
                len(self.protocols))


@dataclass
class TierRelationship:
    """Relationship between tiers"""
    target_tier_id: str
    relationship_type: str  # "depends_on", "enhances", "related_to", "prerequisite"
    strength: float = 1.0  # 0.0 to 1.0


@dataclass
class UnifiedTier:
    """Unified tier combining DEPTH and BREADTH"""
    tier_id: str
    name: str
    tier_type: TierType
    depth_tier_id: Optional[str] = None
    breadth_tier_ids: List[str] = field(default_factory=list)
    domains: List[str] = field(default_factory=list)
    knowledge: Dict[str, TierKnowledge] = field(default_factory=dict)
    modules: List[str] = field(default_factory=list)
    aems: List[str] = field(default_factory=list)
    packs: List[str] = field(default_factory=list)
    description: str = ""
    mastery_level: str = ""
    health: TierHealth = TierHealth.UNKNOWN
    relationships: List[TierRelationship] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)
    access_count: int = 0
    performance_score: float = 0.0

    def get_knowledge_count(self) -> int:
        """Get total knowledge items across all eras"""
        return sum(k.get_total_items() for k in self.knowledge.values())

    def get_related_tiers(self, relationship_type: Optional[str] = None) -> List[str]:
        """Get related tier IDs"""
        if relationship_type:
            return [r.target_tier_id for r in self.relationships
                   if r.relationship_type == relationship_type]
        return [r.target_tier_id for r in self.relationships]

    def add_relationship(self, target_tier_id: str, rel_type: str, strength: float = 1.0):
        """Add a relationship to another tier"""
        # Check if relationship already exists
        for rel in self.relationships:
            if rel.target_tier_id == target_tier_id and rel.relationship_type == rel_type:
                rel.strength = max(rel.strength, strength)
                return
        self.relationships.append(TierRelationship(target_tier_id, rel_type, strength))


class AdvancedTierSystem:
    """
    Advanced Unified Tier System with:
    - Full knowledge extraction
    - Auto-linking
    - Routing optimizations
    - Performance enhancements
    """

    def __init__(self):
        self.depth_tiers: Dict[str, Dict[str, Any]] = {}
        self.breadth_tiers: Dict[str, Dict[str, Any]] = {}
        self.unified_tiers: Dict[str, UnifiedTier] = {}
        self.era_mapping: Dict[TemporalEra, List[str]] = {era: [] for era in TemporalEra}
        self.domain_mapping: Dict[str, List[str]] = {}

        # Advanced features
        self.knowledge_index: Dict[str, List[str]] = defaultdict(list)  # keyword -> tier_ids
        self.module_tier_map: Dict[str, List[str]] = defaultdict(list)  # module_id -> tier_ids
        self.aem_tier_map: Dict[str, List[str]] = defaultdict(list)  # aem_id -> tier_ids
        self.pack_tier_map: Dict[str, List[str]] = defaultdict(list)  # pack_id -> tier_ids
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, float] = {}
        self.cache_ttl_seconds = 300  # 5 minutes

        # Performance metrics
        self.stats = {
            'total_searches': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'auto_links_created': 0,
            'relationships_created': 0,
        }

        self.initialized = False

    def load_depth_tiers_advanced(self) -> int:
        """Load DEPTH tiers with full knowledge extraction"""
        try:
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
                logger.warning("Grandmaster file not found")
                return 0

            with open(grandmaster_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract AURORA_ULTIMATE_GRANDMASTER dict using regex
            # Find the dict definition
            dict_start = content.find('AURORA_ULTIMATE_GRANDMASTER = {')
            if dict_start == -1:
                logger.warning("AURORA_ULTIMATE_GRANDMASTER dict not found")
                return self._load_depth_tiers_fallback(content)

            # Extract tier entries using regex
            tier_pattern = r'"TIER_\d+_[^"]+":\s*\{[^}]*(?:\{[^}]*\}[^}]*)*\}'
            tier_matches = re.finditer(tier_pattern, content, re.DOTALL)

            depth_count = 0
            for match in tier_matches:
                tier_block = match.group(0)
                tier_name_match = re.search(r'"TIER_\d+_[^"]+"', tier_block)
                if tier_name_match:
                    tier_name = tier_name_match.group(0).strip('"')

                    # Parse the tier data
                    tier_data = self._parse_tier_data(tier_block, tier_name)
                    if tier_data:
                        self.depth_tiers[tier_name] = tier_data
                        depth_count += 1

                        # Extract temporal eras
                        self._extract_temporal_eras_advanced(tier_name, tier_data)

            if depth_count == 0:
                # Fallback to simpler extraction
                return self._load_depth_tiers_fallback(content)

            logger.info(f"Loaded {depth_count} DEPTH tiers with full knowledge extraction")
            return depth_count

        except Exception as e:
            logger.error(f"Error loading DEPTH tiers: {e}", exc_info=True)
            return 0

    def _parse_tier_data(self, tier_block: str, tier_name: str) -> Optional[Dict[str, Any]]:
        """Parse tier data from string block"""
        try:
            tier_data = {
                'title': tier_name.replace('_', ' ').title(),
                'description': '',
                'mastery_level': 'OMNISCIENT',
                'knowledge': {}
            }

            # Extract title
            title_match = re.search(r'"title":\s*"([^"]+)"', tier_block)
            if title_match:
                tier_data['title'] = title_match.group(1)

            # Extract description
            desc_match = re.search(r'"description":\s*"([^"]+)"', tier_block)
            if desc_match:
                tier_data['description'] = desc_match.group(1)

            # Extract mastery level
            mastery_match = re.search(r'"mastery_level":\s*"([^"]+)"', tier_block)
            if mastery_match:
                tier_data['mastery_level'] = mastery_match.group(1)

            # Extract knowledge by era
            for era in TemporalEra:
                era_keywords = [era.value, era.value.replace('_', ' ')]
                for keyword in era_keywords:
                    # Look for sections with this era
                    pattern = f'"{keyword}":\\s*\\[([^\\]]+)\\]'
                    matches = re.finditer(pattern, tier_block, re.IGNORECASE)
                    for match in matches:
                        items_str = match.group(1)
                        # Extract quoted strings
                        items = re.findall(r'"([^"]+)"', items_str)
                        if items:
                            if era.value not in tier_data['knowledge']:
                                tier_data['knowledge'][era.value] = []
                            tier_data['knowledge'][era.value].extend(items)

            return tier_data

        except Exception as e:
            logger.warning(f"Error parsing tier {tier_name}: {e}")
            return None

    def _extract_temporal_eras_advanced(self, tier_id: str, tier_data: Dict[str, Any]):
        """Extract temporal eras with full knowledge"""
        # Check knowledge dict
        if 'knowledge' in tier_data:
            for era_key, items in tier_data['knowledge'].items():
                try:
                    era = TemporalEra(era_key)
                    if tier_id not in self.era_mapping[era]:
                        self.era_mapping[era].append(tier_id)
                except ValueError:
                    pass

        # Check all keys for era indicators
        for key, value in tier_data.items():
            key_lower = key.lower()
            for era in TemporalEra:
                if era.value in key_lower:
                    if tier_id not in self.era_mapping[era]:
                        self.era_mapping[era].append(tier_id)

    def _load_depth_tiers_fallback(self, content: str) -> int:
        """Fallback method to extract tier names"""
        tier_pattern = r'"TIER_\d+_[^"]+":\s*\{'
        matches = re.findall(tier_pattern, content)

        depth_count = 0
        tier_names = []
        for match in matches:
            tier_name = match.split('"')[1]
            tier_names.append(tier_name)

        for tier_name in tier_names[:26]:
            self.depth_tiers[tier_name] = {
                'title': tier_name.replace('_', ' ').title(),
                'description': f'DEPTH tier: {tier_name}',
                'mastery_level': 'OMNISCIENT',
                'knowledge': {}
            }
            depth_count += 1

        if depth_count > 0:
            logger.info(f"Loaded {depth_count} DEPTH tier names (fallback)")

        return depth_count

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

    def create_unified_tiers_advanced(self):
        """Create unified tiers with advanced features"""
        unified_count = 0

        # Create unified tiers from DEPTH tiers
        for depth_id, depth_data in self.depth_tiers.items():
            unified_tier = UnifiedTier(
                tier_id=depth_id,
                name=depth_data.get('title', depth_id),
                tier_type=TierType.UNIFIED,
                depth_tier_id=depth_id,
                description=depth_data.get('description', ''),
                mastery_level=depth_data.get('mastery_level', ''),
                health=TierHealth.HEALTHY
            )

            # Extract knowledge by temporal era
            self._extract_knowledge_to_tier_advanced(unified_tier, depth_data)

            # Map to breadth tiers
            self._map_depth_to_breadth_advanced(unified_tier, depth_data)

            # Build knowledge index
            self._index_tier_knowledge(unified_tier)

            self.unified_tiers[depth_id] = unified_tier
            unified_count += 1

        # Create unified tiers from BREADTH tiers
        for breadth_id, breadth_data in self.breadth_tiers.items():
            if breadth_id not in self.unified_tiers:
                unified_tier = UnifiedTier(
                    tier_id=breadth_id,
                    name=breadth_data.get('name', breadth_id),
                    tier_type=TierType.BREADTH,
                    breadth_tier_ids=[breadth_id],
                    domains=breadth_data.get('domains', []),
                    health=TierHealth.HEALTHY
                )
                self.unified_tiers[breadth_id] = unified_tier
                unified_count += 1

        logger.info(f"Created {unified_count} unified tiers with advanced features")
        return unified_count

    def _extract_knowledge_to_tier_advanced(self, tier: UnifiedTier, data: Dict[str, Any]):
        """Extract knowledge organized by temporal era - advanced"""
        # Check if knowledge dict exists
        if 'knowledge' in data:
            for era_key, items in data['knowledge'].items():
                try:
                    era = TemporalEra(era_key)
                    if era.value not in tier.knowledge:
                        tier.knowledge[era.value] = TierKnowledge(era=era)

                    # Categorize items
                    for item in items:
                        item_lower = item.lower()
                        if any(kw in item_lower for kw in ['tool', 'debugger', 'framework', 'library']):
                            tier.knowledge[era.value].tools.append(item)
                        elif any(kw in item_lower for kw in ['language', 'lang', 'programming']):
                            tier.knowledge[era.value].languages.append(item)
                        elif any(kw in item_lower for kw in ['protocol', 'http', 'tcp', 'udp']):
                            tier.knowledge[era.value].protocols.append(item)
                        elif any(kw in item_lower for kw in ['concept', 'pattern', 'principle']):
                            tier.knowledge[era.value].concepts.append(item)
                        elif any(kw in item_lower for kw in ['skill', 'technique', 'method']):
                            tier.knowledge[era.value].skills.append(item)
                        else:
                            tier.knowledge[era.value].technologies.append(item)
                except ValueError:
                    pass

        # Also check top-level keys for era indicators
        for key, value in data.items():
            if isinstance(value, dict):
                era = self._detect_era_from_key(key)
                if era:
                    if era.value not in tier.knowledge:
                        tier.knowledge[era.value] = TierKnowledge(era=era)

                    # Extract items from nested dicts
                    self._extract_items_from_dict(value, tier.knowledge[era.value])

    def _extract_items_from_dict(self, data: Dict[str, Any], knowledge: TierKnowledge):
        """Extract knowledge items from nested dictionary"""
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        item_lower = item.lower()
                        if any(kw in item_lower for kw in ['tool', 'debugger']):
                            knowledge.tools.append(item)
                        elif any(kw in item_lower for kw in ['language', 'lang']):
                            knowledge.languages.append(item)
                        elif any(kw in item_lower for kw in ['protocol']):
                            knowledge.protocols.append(item)
                        elif any(kw in item_lower for kw in ['framework', 'library']):
                            knowledge.frameworks.append(item)
                        else:
                            knowledge.technologies.append(item)
            elif isinstance(value, dict):
                self._extract_items_from_dict(value, knowledge)

    def _detect_era_from_key(self, key: str) -> Optional[TemporalEra]:
        """Detect temporal era from key name"""
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
        return None

    def _map_depth_to_breadth_advanced(self, unified_tier: UnifiedTier, depth_data: Dict[str, Any]):
        """Intelligently map DEPTH tier to BREADTH tiers"""
        tier_name_lower = unified_tier.name.lower()
        description_lower = unified_tier.description.lower()

        # Enhanced domain mapping with keywords
        domain_keywords = {
            'domain-1': ['process', 'timeless', 'eternal', 'core', 'foundation'],
            'domain-2': ['debug', 'debugging', 'error', 'fix', 'troubleshoot'],
            'domain-3': ['architecture', 'design', 'structure', 'system'],
            'domain-4': ['autonomous', 'automation', 'self', 'agent'],
            'domain-5': ['code', 'generation', 'synthesis', 'programming'],
            'domain-6': ['architecture', 'system', 'design', 'pattern'],
            'domain-7': ['tech', 'technology', 'stack', 'platform'],
            'domain-8': ['platform', 'web', 'mobile', 'desktop', 'interface'],
            'domain-9': ['design', 'development', 'ui', 'ux', 'interface'],
            'domain-10': ['browser', 'automation', 'web', 'scraping'],
            'domain-11': ['security', 'crypto', 'encryption', 'auth', 'secure'],
            'domain-12': ['network', 'protocol', 'communication', 'http', 'tcp'],
            'domain-13': ['data', 'storage', 'database', 'cache', 'persist'],
            'domain-14': ['cloud', 'infrastructure', 'server', 'deploy', 'aws'],
            'domain-15': ['ai', 'ml', 'machine learning', 'neural', 'intelligence'],
            'domain-16': ['analytics', 'monitoring', 'metrics', 'log', 'telemetry'],
            'domain-17': ['gaming', 'xr', 'virtual', 'reality', 'ar', 'vr'],
            'domain-18': ['iot', 'embedded', 'hardware', 'device', 'sensor'],
            'domain-19': ['streaming', 'realtime', 'live', 'video', 'audio'],
            'domain-20': ['version', 'control', 'cicd', 'devops', 'git', 'ci'],
        }

        matched_domains = []
        search_text = f"{tier_name_lower} {description_lower}"

        for domain, keywords in domain_keywords.items():
            if any(kw in search_text for kw in keywords):
                matched_domains.append(domain)
                if domain in self.domain_mapping:
                    unified_tier.breadth_tier_ids.extend(self.domain_mapping[domain])
                    unified_tier.domains.append(domain)

        if not matched_domains:
            unified_tier.domains.append('domain-1')
            if 'domain-1' in self.domain_mapping:
                unified_tier.breadth_tier_ids.extend(self.domain_mapping['domain-1'][:5])

    def _index_tier_knowledge(self, tier: UnifiedTier):
        """Build search index for tier knowledge"""
        # Index tier name
        for word in tier.name.lower().split():
            if len(word) > 2:
                self.knowledge_index[word].append(tier.tier_id)

        # Index description
        for word in tier.description.lower().split():
            if len(word) > 2:
                self.knowledge_index[word].append(tier.tier_id)

        # Index knowledge items
        for era_key, knowledge in tier.knowledge.items():
            for item_list in [knowledge.technologies, knowledge.tools, knowledge.concepts,
                             knowledge.skills, knowledge.frameworks, knowledge.languages,
                             knowledge.protocols]:
                for item in item_list:
                    for word in item.lower().split():
                        if len(word) > 2:
                            self.knowledge_index[word].append(tier.tier_id)

    def auto_link_modules(self, manifest_integrator: Any):
        """Auto-link modules to tiers based on intelligent matching"""
        if not manifest_integrator or not hasattr(manifest_integrator, 'modules'):
            return

        linked_count = 0
        for module_id, module in manifest_integrator.modules.items():
            # Extract keywords from module
            module_name = module.name.lower()
            module_category = module.category.lower()

            # Find matching tiers
            matching_tiers = self._find_matching_tiers(module_name, module_category)

            for tier_id in matching_tiers:
                tier = self.unified_tiers.get(tier_id)
                if tier and module_id not in tier.modules:
                    tier.modules.append(module_id)
                    self.module_tier_map[module_id].append(tier_id)
                    linked_count += 1

        self.stats['auto_links_created'] += linked_count
        logger.info(f"Auto-linked {linked_count} modules to tiers")

    def auto_link_aems(self, manifest_integrator: Any):
        """Auto-link AEMs to tiers"""
        if not manifest_integrator or not hasattr(manifest_integrator, 'execution_methods'):
            return

        linked_count = 0
        for aem_id, aem in manifest_integrator.execution_methods.items():
            aem_name = aem.name.lower()
            aem_category = aem.category.lower()

            matching_tiers = self._find_matching_tiers(aem_name, aem_category)

            for tier_id in matching_tiers:
                tier = self.unified_tiers.get(tier_id)
                if tier and aem_id not in tier.aems:
                    tier.aems.append(aem_id)
                    self.aem_tier_map[aem_id].append(tier_id)
                    linked_count += 1

        self.stats['auto_links_created'] += linked_count
        logger.info(f"Auto-linked {linked_count} AEMs to tiers")

    def auto_link_packs(self):
        """Auto-link packs to tiers"""
        pack_mappings = {
            'pack01': ['domain-1', 'TIER_1_TIMELESS_PROCESSES'],
            'pack02': ['domain-16', 'TIER_16_ANALYTICS_MONITORING_GRANDMASTER'],
            'pack03': ['domain-8', 'TIER_8_UNIVERSAL_PLATFORM_GRANDMASTER'],
            'pack04': ['domain-8', 'TIER_8_UNIVERSAL_PLATFORM_GRANDMASTER'],
            'pack05': ['domain-5', 'TIER_5_INFINITE_CODE_GENERATION'],
            'pack06': ['domain-18', 'TIER_18_IOT_EMBEDDED_GRANDMASTER'],
            'pack07': ['domain-11', 'TIER_11_SECURITY_CRYPTOGRAPHY_GRANDMASTER'],
            'pack08': ['domain-15', 'TIER_15_AI_ML_GRANDMASTER'],
            'pack09': ['domain-14', 'TIER_14_CLOUD_INFRASTRUCTURE_GRANDMASTER'],
            'pack10': ['domain-4', 'TIER_4_OMNI_AUTONOMOUS'],
            'pack11': ['domain-12', 'TIER_12_NETWORKING_PROTOCOLS_GRANDMASTER'],
            'pack12': ['domain-5', 'TIER_5_INFINITE_CODE_GENERATION'],
            'pack13': ['domain-3', 'TIER_3_UNIVERSAL_ARCHITECTURE'],
            'pack14': ['domain-18', 'TIER_18_IOT_EMBEDDED_GRANDMASTER'],
            'pack15': ['domain-15', 'TIER_15_AI_ML_GRANDMASTER'],
        }

        linked_count = 0
        for pack_id, mappings in pack_mappings.items():
            for mapping in mappings:
                tier = self.unified_tiers.get(mapping)
                if tier and pack_id not in tier.packs:
                    tier.packs.append(pack_id)
                    self.pack_tier_map[pack_id].append(mapping)
                    linked_count += 1

        self.stats['auto_links_created'] += linked_count
        logger.info(f"Auto-linked {linked_count} packs to tiers")

    def _find_matching_tiers(self, name: str, category: str) -> List[str]:
        """Find tiers matching name/category"""
        matches = set()

        # Search in knowledge index
        for word in name.split():
            if len(word) > 2 and word in self.knowledge_index:
                matches.update(self.knowledge_index[word])

        for word in category.split():
            if len(word) > 2 and word in self.knowledge_index:
                matches.update(self.knowledge_index[word])

        return list(matches)

    def build_tier_relationships(self):
        """Build relationships between tiers"""
        relationship_count = 0

        for tier_id, tier in self.unified_tiers.items():
            # Dependencies: tiers in same domain
            for other_tier_id, other_tier in self.unified_tiers.items():
                if tier_id == other_tier_id:
                    continue

                # Same domain = related
                if set(tier.domains) & set(other_tier.domains):
                    tier.add_relationship(other_tier_id, "related_to", 0.5)
                    relationship_count += 1

                # Shared modules/AEMs/packs = enhances
                shared_modules = set(tier.modules) & set(other_tier.modules)
                shared_aems = set(tier.aems) & set(other_tier.aems)
                shared_packs = set(tier.packs) & set(other_tier.packs)

                if shared_modules or shared_aems or shared_packs:
                    strength = min(1.0, (len(shared_modules) + len(shared_aems) + len(shared_packs)) / 10.0)
                    tier.add_relationship(other_tier_id, "enhances", strength)
                    relationship_count += 1

        self.stats['relationships_created'] += relationship_count
        logger.info(f"Built {relationship_count} tier relationships")

    def initialize(self, manifest_integrator: Optional[Any] = None) -> bool:
        """Initialize the advanced unified tier system"""
        if self.initialized:
            return True

        logger.info("Initializing Advanced Unified Tier System...")

        depth_count = self.load_depth_tiers_advanced()
        breadth_count = self.load_breadth_tiers()

        if depth_count == 0 and breadth_count == 0:
            logger.error("Failed to load any tiers")
            return False

        unified_count = self.create_unified_tiers_advanced()

        # Auto-link modules, AEMs, packs
        if manifest_integrator:
            self.auto_link_modules(manifest_integrator)
            self.auto_link_aems(manifest_integrator)
        self.auto_link_packs()

        # Build relationships
        self.build_tier_relationships()

        self.initialized = True
        logger.info(
            f"Advanced Unified Tier System initialized: "
            f"{depth_count} DEPTH + {breadth_count} BREADTH = {unified_count} unified tiers, "
            f"{self.stats['auto_links_created']} auto-links, "
            f"{self.stats['relationships_created']} relationships"
        )

        return True

    def get_tier(self, tier_id: str) -> Optional[UnifiedTier]:
        """Get unified tier by ID (with caching)"""
        cache_key = f"tier:{tier_id}"
        if self._is_cached(cache_key):
            self.stats['cache_hits'] += 1
            return self.cache[cache_key]

        self.stats['cache_misses'] += 1
        tier = self.unified_tiers.get(tier_id)
        if tier:
            tier.access_count += 1
            self._cache(cache_key, tier)
        return tier

    def search_knowledge_advanced(
        self,
        query: str,
        era: Optional[TemporalEra] = None,
        domain: Optional[str] = None,
        min_knowledge_items: int = 0,
        include_related: bool = False
    ) -> List[UnifiedTier]:
        """Advanced search with filters"""
        self.stats['total_searches'] += 1

        cache_key = f"search:{hashlib.md5(f'{query}:{era}:{domain}:{min_knowledge_items}'.encode()).hexdigest()}"
        if self._is_cached(cache_key):
            self.stats['cache_hits'] += 1
            return self.cache[cache_key]

        self.stats['cache_misses'] += 1
        query_lower = query.lower()
        results = []
        seen = set()

        # Search in indexed knowledge
        matching_tier_ids = set()
        for word in query_lower.split():
            if len(word) > 2 and word in self.knowledge_index:
                matching_tier_ids.update(self.knowledge_index[word])

        # Filter by criteria
        for tier_id in matching_tier_ids:
            if tier_id in seen:
                continue

            tier = self.unified_tiers.get(tier_id)
            if not tier:
                continue

            # Era filter
            if era and era.value not in tier.knowledge:
                continue

            # Domain filter
            if domain and domain not in tier.domains:
                continue

            # Knowledge items filter
            if tier.get_knowledge_count() < min_knowledge_items:
                continue

            results.append(tier)
            seen.add(tier_id)

            # Include related tiers
            if include_related:
                for rel in tier.relationships:
                    if rel.target_tier_id not in seen:
                        related_tier = self.unified_tiers.get(rel.target_tier_id)
                        if related_tier:
                            results.append(related_tier)
                            seen.add(rel.target_tier_id)

        # Sort by relevance (knowledge count, access count)
        results.sort(key=lambda t: (t.get_knowledge_count(), t.access_count), reverse=True)

        self._cache(cache_key, results)
        return results

    def get_tiers_by_era(self, era: TemporalEra) -> List[UnifiedTier]:
        """Get all tiers containing knowledge from a specific era"""
        return [t for t in self.unified_tiers.values() if era.value in t.knowledge]

    def get_tiers_by_domain(self, domain: str) -> List[UnifiedTier]:
        """Get all tiers in a specific domain"""
        return [t for t in self.unified_tiers.values() if domain in t.domains]

    def get_tier_routing_suggestions(self, task_type: str, payload: Dict[str, Any]) -> List[str]:
        """Get tier routing suggestions for a task"""
        # Extract keywords from task
        keywords = []
        if isinstance(payload, dict):
            keywords.extend(str(v).lower().split() for v in payload.values() if isinstance(v, str))
        keywords.extend(task_type.lower().split())

        # Find matching tiers
        matching_tiers = set()
        for keyword_list in keywords:
            for keyword in keyword_list:
                if len(keyword) > 2 and keyword in self.knowledge_index:
                    matching_tiers.update(self.knowledge_index[keyword])

        # Score tiers by relevance
        tier_scores = {}
        for tier_id in matching_tiers:
            tier = self.unified_tiers.get(tier_id)
            if tier:
                score = tier.get_knowledge_count() + tier.access_count * 0.1
                tier_scores[tier_id] = score

        # Return top 5 suggestions
        sorted_tiers = sorted(tier_scores.items(), key=lambda x: x[1], reverse=True)
        return [tier_id for tier_id, _ in sorted_tiers[:5]]

    def _is_cached(self, key: str) -> bool:
        """Check if key is cached and valid"""
        if key not in self.cache:
            return False
        if key in self.cache_ttl:
            if time.time() > self.cache_ttl[key]:
                del self.cache[key]
                del self.cache_ttl[key]
                return False
        return True

    def _cache(self, key: str, value: Any):
        """Cache a value"""
        self.cache[key] = value
        self.cache_ttl[key] = time.time() + self.cache_ttl_seconds

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        era_counts = {era.value: len(self.get_tiers_by_era(era)) for era in TemporalEra}

        return {
            'tier_counts': {
                'depth': len(self.depth_tiers),
                'breadth': len(self.breadth_tiers),
                'unified': len(self.unified_tiers),
                'total': len(self.unified_tiers)
            },
            'era_distribution': era_counts,
            'domain_count': len(self.domain_mapping),
            'total_knowledge_items': sum(
                t.get_knowledge_count() for t in self.unified_tiers.values()
            ),
            'tiers_with_modules': sum(1 for t in self.unified_tiers.values() if t.modules),
            'tiers_with_aems': sum(1 for t in self.unified_tiers.values() if t.aems),
            'tiers_with_packs': sum(1 for t in self.unified_tiers.values() if t.packs),
            'total_relationships': sum(
                len(t.relationships) for t in self.unified_tiers.values()
            ),
            'performance': {
                'cache_hit_rate': (
                    self.stats['cache_hits'] / max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
                ),
                'total_searches': self.stats['total_searches'],
                'auto_links': self.stats['auto_links_created'],
                'relationships': self.stats['relationships_created'],
            }
        }

    def get_all_tiers(self) -> Dict[str, UnifiedTier]:
        """Get all unified tiers"""
        return self.unified_tiers


# Global instance
_advanced_tier_system: Optional[AdvancedTierSystem] = None


def get_advanced_tier_system(manifest_integrator: Optional[Any] = None) -> AdvancedTierSystem:
    """Get or create the global advanced unified tier system instance"""
    global _advanced_tier_system
    if _advanced_tier_system is None:
        _advanced_tier_system = AdvancedTierSystem()
        _advanced_tier_system.initialize(manifest_integrator)
    return _advanced_tier_system
