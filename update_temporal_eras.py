#!/usr/bin/env python3
"""
Update Cross-Temporal Modules with Temporal Era Assignments

Issue: #23 - Implement Cross-Temporal Modules (550 modules)
Issue: #45 - Complete temporal tier coverage

This script updates the modules manifest to assign temporal eras to all 550 modules,
distributing them evenly across 5 temporal eras (110 modules per era).
"""

import json
from pathlib import Path
from typing import List, Dict, Any

# Temporal eras (matching manifest_integrator.py)
TEMPORAL_ERAS = ["Ancient", "Classical", "Modern", "Futuristic", "Post-Quantum"]

# Module categories for better distribution
CATEGORIES = [
    "analyzer", "connector", "formatter", "generator", "integrator",
    "monitor", "optimizer", "processor", "transformer", "validator"
]


def assign_temporal_era(module_id: int, category: str) -> str:
    """
    Assign temporal era based on module ID and category
    
    Distribution strategy:
    - Modules 1-110: Ancient (1950s-1980s)
    - Modules 111-220: Classical (1990s-2000s)
    - Modules 221-330: Modern (2010s-2020s)
    - Modules 331-440: Futuristic (2020s-2030s)
    - Modules 441-550: Post-Quantum (Post-singularity)
    """
    if module_id <= 110:
        return "Ancient"
    elif module_id <= 220:
        return "Classical"
    elif module_id <= 330:
        return "Modern"
    elif module_id <= 440:
        return "Futuristic"
    else:
        return "Post-Quantum"


def update_modules_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Update modules manifest with temporal era assignments"""
    
    # Load existing manifest
    with open(manifest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modules = data.get("modules", [])
    
    if len(modules) != 550:
        print(f"Warning: Expected 550 modules, found {len(modules)}")
    
    # Update each module with temporal era
    era_counts = {era: 0 for era in TEMPORAL_ERAS}
    
    for module in modules:
        module_id = module.get("id", 0)
        category = module.get("category", "")
        
        # Assign temporal era
        temporal_era = assign_temporal_era(module_id, category)
        module["temporalEra"] = temporal_era
        era_counts[temporal_era] += 1
        
        # Ensure other required fields exist
        if "name" not in module:
            module["name"] = f"module-{module_id}"
        if "category" not in module or not module["category"]:
            # Assign category based on module ID
            cat_index = (module_id - 1) % len(CATEGORIES)
            module["category"] = CATEGORIES[cat_index]
        if "status" not in module:
            module["status"] = "active"
        if "version" not in module:
            module["version"] = "1.0.0"
        if "supportedDevices" not in module:
            module["supportedDevices"] = []
        if "entrypoints" not in module:
            module["entrypoints"] = {}
        if "sandbox" not in module:
            module["sandbox"] = "vm"
        if "permissions" not in module:
            module["permissions"] = []
        if "dependencies" not in module:
            module["dependencies"] = []
        if "metadata" not in module:
            module["metadata"] = {}
    
    # Add metadata about temporal distribution
    data["metadata"] = {
        "total_modules": len(modules),
        "temporal_era_distribution": era_counts,
        "temporal_eras": TEMPORAL_ERAS,
        "updated": "2025-12-20"
    }
    
    return data, era_counts


def main():
    """Main execution"""
    manifest_path = Path("manifests/modules.manifest.json")
    
    if not manifest_path.exists():
        print(f"Error: Manifest file not found: {manifest_path}")
        return
    
    print("=" * 60)
    print("Cross-Temporal Modules Update")
    print("=" * 60)
    print(f"\nUpdating: {manifest_path}")
    
    # Update manifest
    updated_data, era_counts = update_modules_manifest(manifest_path)
    
    # Backup original
    backup_path = manifest_path.with_suffix('.manifest.json.backup')
    print(f"\nCreating backup: {backup_path}")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    # Write updated manifest
    print(f"Writing updated manifest...")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("UPDATE SUMMARY")
    print("=" * 60)
    print(f"Total modules: {len(updated_data['modules'])}")
    print("\nTemporal Era Distribution:")
    for era, count in sorted(era_counts.items()):
        print(f"  {era:20s}: {count:3d} modules")
    
    print("\n[OK] Modules manifest updated successfully!")
    print(f"[OK] Backup saved to: {backup_path}")
    print("\nAll 550 modules now have temporal era assignments.")


if __name__ == "__main__":
    main()
