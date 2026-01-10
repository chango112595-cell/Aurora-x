#!/usr/bin/env python3
"""Test temporal era integration with manifest integrator"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from aurora_nexus_v3.core.manifest_integrator import ManifestIntegrator
from collections import defaultdict

async def test_integration():
    """Test that manifest integrator loads temporal eras correctly"""
    print("=" * 60)
    print("Temporal Era Integration Test")
    print("=" * 60)

    mi = ManifestIntegrator()
    await mi.initialize()

    print(f"\nLoaded modules: {mi.module_count}")

    # Count modules by temporal era
    eras = defaultdict(int)
    for module in mi.modules.values():
        era = module.metadata.get('temporal_era', 'Unknown')
        eras[era] += 1

    print("\nTemporal Era Distribution (from ManifestIntegrator):")
    for era in sorted(eras.keys()):
        count = eras[era]
        print(f"  {era:20s}: {count:3d} modules")

    # Verify all modules have temporal era
    modules_without_era = [
        m for m in mi.modules.values()
        if not m.metadata.get('temporal_era')
    ]

    if modules_without_era:
        print(f"\n[WARNING] {len(modules_without_era)} modules without temporal era")
    else:
        print("\n[OK] All modules have temporal era assignments")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_integration())
