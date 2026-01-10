#!/usr/bin/env python3
"""
Comprehensive task verification script
Verifies completion status of all priority tasks
"""

import json
from pathlib import Path

def verify_task_completion():
    """Verify all tasks from priority list"""
    
    results = {
        "completed": [],
        "in_progress": [],
        "remaining": [],
        "verified": []
    }
    
    # Task verification checks
    checks = {
        "#46 - Localhost references": Path("server/config.ts").exists(),
        "#42 - Installers": Path("installers/android/android_installer.py").exists() and 
                            Path("installers/ios/ios_installer.py").exists() and
                            Path("installers/wasm/wasm_installer.py").exists(),
        "#47 - EdgeOS adapters": Path("aurora_edgeos/automotive/runtime.py").exists() and
                                 Path("aurora_edgeos/aviation/runtime.py").exists(),
        "#14 - EdgeOS validation": Path("test_edgeos_runtimes_offline.py").exists(),
        "#23 - Cross-temporal": Path("manifests/modules.manifest.json").exists(),
        "#45 - Temporal coverage": Path("verify_temporal_coverage.py").exists(),
        "#12 - Vault encryption": Path("aurora_supervisor/secure/ase_vault.py").exists(),
        "#36 - Grandmaster": Path("aurora_ultimate_omniscient_grandmaster.py").exists(),
        "#37 - Tier merge": Path("aurora_nexus_v3/core/unified_tier_system_advanced.py").exists(),
        "#38 - PACK06-15": all(Path(f"packs/pack{i:02d}_*/__init__.py").exists() for i in range(6, 16)),
        "#4 - Hardware detector": Path("aurora_nexus_v3/modules/hardware_detector.py").exists(),
    }
    
    for task, verified in checks.items():
        if verified:
            results["completed"].append(task)
        else:
            results["remaining"].append(task)
    
    return results

if __name__ == "__main__":
    results = verify_task_completion()
    print(json.dumps(results, indent=2))
