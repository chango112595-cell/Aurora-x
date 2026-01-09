#!/usr/bin/env python3
"""Verify temporal era coverage for all 550 modules"""

import json
from pathlib import Path
from collections import defaultdict

manifest_path = Path("manifests/modules.manifest.json")

with open(manifest_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

modules = data.get("modules", [])
era_counts = defaultdict(int)
category_counts = defaultdict(int)

for module in modules:
    era = module.get("temporalEra", "Unknown")
    category = module.get("category", "Unknown")
    era_counts[era] += 1
    category_counts[category] += 1

print("=" * 60)
print("Temporal Era Coverage Verification")
print("=" * 60)
print(f"\nTotal modules: {len(modules)}")
print("\nTemporal Era Distribution:")
for era in sorted(era_counts.keys()):
    count = era_counts[era]
    percentage = (count / len(modules)) * 100
    print(f"  {era:20s}: {count:3d} modules ({percentage:5.1f}%)")

print("\nCategory Distribution (top 10):")
for category, count in sorted(category_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"  {category:20s}: {count:3d} modules")

# Verify all modules have temporal era
modules_without_era = [m for m in modules if not m.get("temporalEra")]
if modules_without_era:
    print(f"\n[WARNING] {len(modules_without_era)} modules without temporal era")
else:
    print("\n[OK] All modules have temporal era assignments")

# Check metadata
metadata = data.get("metadata", {})
if metadata:
    print("\nManifest Metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

print("\n" + "=" * 60)
