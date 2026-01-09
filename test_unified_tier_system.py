#!/usr/bin/env python3
"""
Test script for Unified Tier System
Verifies that 26-tier DEPTH and 188-tier BREADTH are properly merged
"""

import asyncio
import sys
from pathlib import Path

# Add aurora_nexus_v3 to path
sys.path.insert(0, str(Path(__file__).parent))

from aurora_nexus_v3.core.unified_tier_system import (
    get_unified_tier_system,
    TemporalEra,
)


async def test_unified_tier_system():
    """Test the unified tier system"""
    print("=" * 80)
    print("AURORA UNIFIED TIER SYSTEM TEST")
    print("=" * 80)
    print()
    
    # Initialize system
    print("1. Initializing Unified Tier System...")
    tier_system = get_unified_tier_system()
    
    if not tier_system.initialized:
        print("   ERROR: Failed to initialize unified tier system")
        return False
    
    print("   [OK] Unified Tier System initialized")
    print()
    
    # Get statistics
    print("2. Getting statistics...")
    stats = tier_system.get_statistics()
    print(f"   Tier counts:")
    print(f"     - DEPTH tiers: {stats['tier_counts']['depth']}")
    print(f"     - BREADTH tiers: {stats['tier_counts']['breadth']}")
    print(f"     - Unified tiers: {stats['tier_counts']['unified']}")
    print(f"     - Total: {stats['tier_counts']['total']}")
    print()
    
    print(f"   Temporal era distribution:")
    for era, count in stats['era_distribution'].items():
        print(f"     - {era}: {count} tiers")
    print()
    
    print(f"   Knowledge items:")
    print(f"     - Total knowledge items: {stats['total_knowledge_items']}")
    print(f"     - Tiers with modules: {stats['tiers_with_modules']}")
    print(f"     - Tiers with AEMs: {stats['tiers_with_aems']}")
    print(f"     - Tiers with packs: {stats['tiers_with_packs']}")
    print()
    
    # Test getting specific tiers
    print("3. Testing tier retrieval...")
    depth_tiers = [t for t in tier_system.get_all_tiers().values() if t.depth_tier_id]
    breadth_tiers = [t for t in tier_system.get_all_tiers().values() if t.breadth_tier_ids]
    
    print(f"   Found {len(depth_tiers)} tiers with DEPTH knowledge")
    print(f"   Found {len(breadth_tiers)} tiers with BREADTH mapping")
    print()
    
    # Test temporal era access
    print("4. Testing temporal era access...")
    for era in TemporalEra:
        tiers = tier_system.get_tiers_by_era(era)
        print(f"   {era.value}: {len(tiers)} tiers")
    print()
    
    # Test knowledge search
    print("5. Testing knowledge search...")
    search_queries = ["debugging", "security", "networking", "cloud", "ai"]
    for query in search_queries:
        results = tier_system.search_knowledge(query)
        print(f"   '{query}': {len(results)} tiers found")
    print()
    
    # Test domain access
    print("6. Testing domain access...")
    domain_tiers = tier_system.get_tiers_by_domain("domain-11")  # Security domain
    print(f"   Domain 'domain-11' (Security): {len(domain_tiers)} tiers")
    print()
    
    # Show sample unified tier
    print("7. Sample unified tier structure...")
    all_tiers = tier_system.get_all_tiers()
    if all_tiers:
        sample_tier = list(all_tiers.values())[0]
        print(f"   Tier ID: {sample_tier.tier_id}")
        print(f"   Name: {sample_tier.name}")
        print(f"   Type: {sample_tier.tier_type.value}")
        print(f"   DEPTH tier: {sample_tier.depth_tier_id}")
        print(f"   BREADTH tiers: {len(sample_tier.breadth_tier_ids)}")
        print(f"   Domains: {sample_tier.domains}")
        print(f"   Knowledge eras: {list(sample_tier.knowledge.keys())}")
        print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    # Verify counts
    if stats['tier_counts']['depth'] >= 26 and stats['tier_counts']['breadth'] >= 188:
        print("[SUCCESS] Unified Tier System is properly merged!")
        return True
    else:
        print("[WARNING] Some tiers may be missing")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_unified_tier_system())
    sys.exit(0 if success else 1)
