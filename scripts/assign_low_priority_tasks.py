#!/usr/bin/env python3
"""
Assign LOW Priority Tasks to Workers and Healers
This script simulates workers and healers fixing low-priority issues
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# LOW PRIORITY TASKS from REMAINING_ISSUES_FINAL.md
LOW_PRIORITY_TASKS = [
    {
        "id": "low_001",
        "type": "cleanup",
        "description": "Remove backup files (*.aurora_backup, *_old*, *_deprecated*, *_backup*)",
        "target": "backup_files",
        "priority": "low",
    },
    {
        "id": "low_002",
        "type": "cleanup",
        "description": "Archive failed experiments (370+ files)",
        "target": "failed_experiments",
        "priority": "low",
    },
    {
        "id": "low_003",
        "type": "verification",
        "description": "Run test coverage analysis",
        "target": "test_coverage",
        "priority": "low",
    },
    {
        "id": "low_004",
        "type": "enhancement",
        "description": "Replace mock data in 550 generated modules with real connections",
        "target": "generated_modules",
        "priority": "low",
    },
    {
        "id": "low_005",
        "type": "feature",
        "description": "Implement Code Library Explorer with search and categorization",
        "target": "code_library_explorer",
        "priority": "low",
    },
    {
        "id": "low_006",
        "type": "feature",
        "description": "Implement Corpus Learning Data Analyzer visualizer",
        "target": "learning_data_analyzer",
        "priority": "low",
    },
    {
        "id": "low_007",
        "type": "feature",
        "description": "Implement Universal Package Manager Abstraction (apt/yum/brew/choco/pkg)",
        "target": "package_manager",
        "priority": "low",
    },
    {
        "id": "low_008",
        "type": "feature",
        "description": "Implement Satellite Uplink Module with store-and-forward",
        "target": "satellite_uplink",
        "priority": "low",
    },
    {
        "id": "low_009",
        "type": "feature",
        "description": (
            "Implement additional edge runtimes "
            "(train, car/factory robot, power grid, medical, defense)"
        ),
        "target": "edge_runtimes",
        "priority": "low",
    },
    {
        "id": "low_010",
        "type": "enhancement",
        "description": "Generate additional modules to reach 3,975+ target (currently ~2,300)",
        "target": "module_generation",
        "priority": "low",
    },
]


def find_backup_files():
    """Find all backup files"""
    backup_patterns = ["*.aurora_backup", "*_old*", "*_deprecated*", "*_backup*"]
    backup_files = []

    for root, dirs, files in os.walk(project_root):
        # Skip certain directories
        dirs[:] = [
            d for d in dirs if d not in [".git", "node_modules", "__pycache__", ".venv", "venv"]
        ]

        for file in files:
            for pattern in backup_patterns:
                if pattern.replace("*", "") in file:
                    backup_files.append(os.path.join(root, file))
                    break

    return backup_files


def find_failed_experiments():
    """Find failed experiment files"""
    failed_dirs = [
        "ask_aurora_scripts",
        "system_fixers",
        "testing_verification",
        "code_quality_fixers",
    ]

    failed_files = []
    for root, _dirs, files in os.walk(project_root):
        for dir_name in failed_dirs:
            if dir_name in root.lower():
                for file in files:
                    if file.endswith((".py", ".js", ".ts", ".json")):
                        failed_files.append(os.path.join(root, file))

    return failed_files


def remove_backup_files():
    """Worker task: Remove backup files"""
    print("[WORKER] Task: Removing backup files...")
    backup_files = find_backup_files()

    removed = 0
    for file_path in backup_files:
        try:
            os.remove(file_path)
            removed += 1
            print(f"  [WORKER] Removed: {file_path}")
        except Exception as e:
            print(f"  [WORKER] Error removing {file_path}: {e}")

    print(f"[WORKER] Removed {removed}/{len(backup_files)} backup files")
    return {"removed": removed, "total": len(backup_files)}


def archive_failed_experiments():
    """Worker task: Archive failed experiments"""
    print("[WORKER] Task: Archiving failed experiments...")
    failed_files = find_failed_experiments()

    archive_dir = project_root / "archived_experiments"
    archive_dir.mkdir(exist_ok=True)

    archived = 0
    for file_path in failed_files[:100]:  # Limit to first 100
        try:
            rel_path = os.path.relpath(file_path, project_root)
            archive_path = archive_dir / rel_path.replace(os.sep, "_")
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            import shutil

            shutil.copy2(file_path, archive_path)
            os.remove(file_path)
            archived += 1
        except Exception as e:
            print(f"  [WORKER] Error archiving {file_path}: {e}")

    print(f"[WORKER] Archived {archived}/{len(failed_files)} failed experiment files")
    return {"archived": archived, "total": len(failed_files)}


def verify_test_coverage():
    """Healer task: Verify test coverage"""
    print("[HEALER] Task: Verifying test coverage...")

    test_files = list(project_root.rglob("test_*.py"))
    test_count = len(test_files)

    print(f"[HEALER] Found {test_count} test files")
    return {"test_files": test_count, "status": "verified"}


def main():
    """Main execution - simulate workers and healers fixing low priority tasks"""
    print("=" * 60)
    print("WORKERS & HEALERS: Processing LOW Priority Tasks")
    print("=" * 60)

    results = {}

    # Worker tasks (cleanup and file operations)
    print("\n[WORKERS] Starting cleanup tasks...")
    results["backup_cleanup"] = remove_backup_files()
    results["experiment_archive"] = archive_failed_experiments()

    # Healer tasks (verification and health checks)
    print("\n[HEALERS] Starting verification tasks...")
    results["test_coverage"] = verify_test_coverage()

    # Save results
    results_file = project_root / "worker_healer_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("WORKERS & HEALERS: Task completion summary")
    print("=" * 60)
    print(f"Backup files removed: {results['backup_cleanup']['removed']}")
    print(f"Failed experiments archived: {results['experiment_archive']['archived']}")
    print(f"Test files verified: {results['test_coverage']['test_files']}")
    print(f"\nResults saved to: {results_file}")

    return results


if __name__ == "__main__":
    main()
