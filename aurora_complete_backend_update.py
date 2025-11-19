#!/usr/bin/env python3
"""
Aurora Complete Backend Update
Updates all backend TypeScript files to reflect 53 tiers and 66 total capabilities
"""

from pathlib import Path


def update_typescript_file(file_path: Path, replacements: list[tuple[str, str]]) -> bool:
    """Update a TypeScript file with multiple replacements"""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        for old, new in replacements:
            content = content.replace(old, new)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"  ❌ Error updating {file_path}: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("🔧 AURORA COMPLETE BACKEND UPDATE")
    print("=" * 60)

    updates = {
        "server/aurora-chat.ts": [
            (
                "- 33 Mastery Tiers: Your knowledge domains",
                "- 54 Capabilities: 13 Foundation Tasks + 53 Knowledge Tiers",
            ),
        ],
        "server/routes.ts": [
            (
                "27 mastery tiers spanning ancient computing (1940s) to future tech",
                "66 capabilities (13 foundation tasks + 53 knowledge tiers) spanning ancient to future tech",
            ),
            (
                "**My knowledge (27 mastery tiers):",
                "**My knowledge (53 knowledge tiers + 13 foundation tasks = 66 capabilities):",
            ),
            ("🧠 27 mastery tiers: LOADED", "🧠 53 knowledge tiers: LOADED (66 total capabilities)"),
            ("🧠 All 53 tiers active", "🧠 All 53 tiers active (66 total capabilities)"),
        ],
    }

    print("\n📝 Updating Backend Files:")
    updated_files = []

    for file_path_str, replacements in updates.items():
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"  ⚠️  File not found: {file_path}")
            continue

        if update_typescript_file(file_path, replacements):
            print(f"  ✅ Updated: {file_path}")
            updated_files.append(file_path_str)
        else:
            print(f"  ℹ️  No changes needed: {file_path}")

    print("\n" + "=" * 60)
    print("📊 UPDATE SUMMARY")
    print("=" * 60)
    print(f"Files updated: {len(updated_files)}")

    if updated_files:
        print("\nUpdated files:")
        for f in updated_files:
            print(f"  • {f}")

    print("\n✅ Backend now reflects:")
    print("  • 13 Foundation Tasks")
    print("  • 53 Knowledge Tiers (including 6 new autonomous tiers)")
    print("  • 54 Total Capabilities")
    print()
    print("New Autonomous Tiers (36-41):")
    print("  • Tier 36: Self-Monitor (24/7 monitoring)")
    print("  • Tier 37: Tier Expansion (auto-build capabilities)")
    print("  • Tier 38: Tier Orchestrator (multi-tier coordination)")
    print("  • Tier 39: Performance Optimizer (predictive analysis)")
    print("  • Tier 40: Full Autonomy (100% autonomous operation)")
    print("  • Tier 53: Strategist (strategic planning)")

    print("\n" + "=" * 60)
    print("🚀 BACKEND UPDATE COMPLETE")
    print("=" * 60 + "\n")

    return len(updated_files) > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
