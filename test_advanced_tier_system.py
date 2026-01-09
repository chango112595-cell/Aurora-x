#!/usr/bin/env python3
"""
Test script for Advanced Unified Tier System
Tests all advanced features: full knowledge extraction, auto-linking, routing optimizations
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from aurora_nexus_v3.core.unified_tier_system_advanced import (
    get_advanced_tier_system,
    TemporalEra,
)


async def test_advanced_tier_system():
    """Test the advanced unified tier system"""
    print("=" * 80)
    print("AURORA ADVANCED UNIFIED TIER SYSTEM TEST")
    print("=" * 80)
    print()

    # Initialize system
    print("1. Initializing Advanced Unified Tier System...")
    tier_system = get_advanced_tier_system()

    if not tier_system.initialized:
        print("   ERROR: Failed to initialize advanced unified tier system")
        return False

    print("   [OK] Advanced Unified Tier System initialized")
    print()

    # Get statistics
    print("2. Getting comprehensive statistics...")
    stats = tier_system.get_statistics()
    print(f"   Tier counts:")
    print(f"     - DEPTH tiers: {stats['tier_counts']['depth']}")
    print(f"     - BREADTH tiers: {stats['tier_counts']['breadth']}")
    print(f"     - Unified tiers: {stats['tier_counts']['unified']}")
    print(f"     - Total: {stats['tier_counts']['total']}")
    print()

    print(f"   Temporal era distribution:")
    for era, count in stats['era_distribution'].items():
        print(f"     - {era:15} {count:3} tiers")
    print()

    print(f"   Knowledge and links:")
    print(f"     - Total knowledge items: {stats['total_knowledge_items']}")
    print(f"     - Tiers with modules: {stats['tiers_with_modules']}")
    print(f"     - Tiers with AEMs: {stats['tiers_with_aems']}")
    print(f"     - Tiers with packs: {stats['tiers_with_packs']}")
    print(f"     - Total relationships: {stats['total_relationships']}")
    print()

    print(f"   Performance metrics:")
    perf = stats['performance']
    print(f"     - Cache hit rate: {perf['cache_hit_rate']:.2%}")
    print(f"     - Total searches: {perf['total_searches']}")
    print(f"     - Auto-links created: {perf['auto_links']}")
    print(f"     - Relationships created: {perf['relationships']}")
    print()

    # Test advanced search
    print("3. Testing advanced search capabilities...")
    search_queries = [
        ("debugging", None, None),
        ("security", TemporalEra.MODERN, None),
        ("networking", None, "domain-12"),
        ("cloud", TemporalEra.MODERN, "domain-14"),
    ]

    for query, era, domain in search_queries:
        results = tier_system.search_knowledge_advanced(
            query, era, domain, min_knowledge_items=0, include_related=False
        )
        era_str = era.value if era else "any"
        domain_str = domain if domain else "any"
        print(f"   '{query}' (era={era_str}, domain={domain_str}): {len(results)} tiers")
    print()

    # Test tier routing suggestions
    print("4. Testing tier routing suggestions...")
    test_tasks = [
        ("debug", {"action": "debug", "error": "memory leak"}),
        ("security", {"action": "encrypt", "data": "sensitive"}),
        ("network", {"action": "connect", "protocol": "http"}),
    ]

    for task_type, payload in test_tasks:
        suggestions = tier_system.get_tier_routing_suggestions(task_type, payload)
        print(f"   Task '{task_type}': {len(suggestions)} suggestions")
        if suggestions:
            print(f"     Top suggestion: {suggestions[0]}")
    print()

    # Test tier relationships
    print("5. Testing tier relationships...")
    all_tiers = tier_system.get_all_tiers()
    tiers_with_relationships = [t for t in all_tiers.values() if t.relationships]
    print(f"   Tiers with relationships: {len(tiers_with_relationships)}")
    if tiers_with_relationships:
        sample_tier = tiers_with_relationships[0]
        print(f"   Sample tier '{sample_tier.tier_id}':")
        print(f"     - {len(sample_tier.relationships)} relationships")
        print(f"     - Related tiers: {sample_tier.get_related_tiers()[:3]}")
    print()

    # Test knowledge extraction
    print("6. Testing knowledge extraction...")
    depth_tiers = [t for t in all_tiers.values() if t.depth_tier_id]
    print(f"   DEPTH tiers with knowledge: {len(depth_tiers)}")
    if depth_tiers:
        sample_tier = depth_tiers[0]
        print(f"   Sample tier '{sample_tier.tier_id}':")
        print(f"     - Knowledge eras: {list(sample_tier.knowledge.keys())}")
        total_knowledge = sample_tier.get_knowledge_count()
        print(f"     - Total knowledge items: {total_knowledge}")
        if sample_tier.knowledge:
            era_key = list(sample_tier.knowledge.keys())[0]
            knowledge = sample_tier.knowledge[era_key]
            print(f"     - Sample era '{era_key}':")
            print(f"       Technologies: {len(knowledge.technologies)}")
            print(f"       Tools: {len(knowledge.tools)}")
            print(f"       Concepts: {len(knowledge.concepts)}")
            print(f"       Skills: {len(knowledge.skills)}")
    print()

    # Test caching
    print("7. Testing caching performance...")
    initial_hits = tier_system.stats['cache_hits']
    initial_misses = tier_system.stats['cache_misses']

    # Perform multiple searches
    for _ in range(10):
        tier_system.search_knowledge_advanced("debugging")
        tier_system.get_tier("TIER_2_ETERNAL_DEBUGGING")

    final_hits = tier_system.stats['cache_hits']
    final_misses = tier_system.stats['cache_misses']

    hits_added = final_hits - initial_hits
    misses_added = final_misses - initial_misses

    print(f"   Cache hits added: {hits_added}")
    print(f"   Cache misses added: {misses_added}")
    if hits_added + misses_added > 0:
        hit_rate = hits_added / (hits_added + misses_added)
        print(f"   Cache hit rate: {hit_rate:.2%}")
    print()

    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

    # Verify all features
    checks = [
        (stats['tier_counts']['depth'] >= 26, "DEPTH tiers loaded"),
        (stats['tier_counts']['breadth'] >= 188, "BREADTH tiers loaded"),
        (stats['tiers_with_packs'] > 0, "Packs auto-linked"),
        (stats['total_relationships'] > 0, "Relationships built"),
        (perf['auto_links'] > 0, "Auto-linking working"),
    ]

    all_passed = all(check[0] for check in checks)

    print("\nFeature verification:")
    for passed, feature in checks:
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {feature}")

    if all_passed:
        print("\n[SUCCESS] All advanced features are working!")
        return True
    else:
        print("\n[WARNING] Some features may need attention")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_advanced_tier_system())
    sys.exit(0 if success else 1)
