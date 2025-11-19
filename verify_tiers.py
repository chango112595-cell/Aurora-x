#!/usr/bin/env python3
"""Quick verification that tiers 47-50 are loaded"""

from aurora_core import AuroraKnowledgeTiers

a = AuroraKnowledgeTiers()

print(f"✅ Total Tiers: {a.tier_count}")
print(f"✅ Foundation Count: {a.foundation_count}")
print(f"✅ Total Capabilities: {a.total_capabilities}")

print("\n🎯 Tiers 47-50 Status:")
print(f"  Tier 47 (Doc Generator): {'✅ Loaded' if 'tier_47_doc_generator' in a.tiers else '❌ Missing'}")
print(f"  Tier 48 (Multi-Agent): {'✅ Loaded' if 'tier_48_multi_agent' in a.tiers else '❌ Missing'}")
print(f"  Tier 49 (UI Generator): {'✅ Loaded' if 'tier_49_ui_generator' in a.tiers else '❌ Missing'}")
print(f"  Tier 50 (Git Master): {'✅ Loaded' if 'tier_50_git_master' in a.tiers else '❌ Missing'}")

print("\n🔥 Bonus Tiers:")
print(f"  Tier 51 (Code Quality): {'✅ Loaded' if 'tier_51_code_quality' in a.tiers else '❌ Missing'}")
print(f"  Tier 52 (RSA Grandmaster): {'✅ Loaded' if 'tier_52_rsa_grandmaster' in a.tiers else '❌ Missing'}")
print(f"  Tier 53 (Docker Master): {'✅ Loaded' if 'tier_53_docker_master' in a.tiers else '❌ Missing'}")
