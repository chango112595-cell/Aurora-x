#!/usr/bin/env python3
"""Quick verification of tier system merge"""

from aurora_nexus_v3.core.unified_tier_system import get_unified_tier_system

ts = get_unified_tier_system()
stats = ts.get_statistics()

print("=" * 60)
print("UNIFIED TIER SYSTEM STATUS")
print("=" * 60)
print(f"DEPTH tiers:     {stats['tier_counts']['depth']}")
print(f"BREADTH tiers:   {stats['tier_counts']['breadth']}")
print(f"Unified tiers:   {stats['tier_counts']['unified']}")
print(f"Total:           {stats['tier_counts']['total']}")
print()
print("Temporal Era Distribution:")
for era, count in stats['era_distribution'].items():
    print(f"  {era:15} {count:3} tiers")
print()
print("Knowledge:")
print(f"  Total items:   {stats['total_knowledge_items']}")
print(f"  With modules:  {stats['tiers_with_modules']}")
print(f"  With AEMs:     {stats['tiers_with_aems']}")
print(f"  With packs:    {stats['tiers_with_packs']}")
print("=" * 60)
