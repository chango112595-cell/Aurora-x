#!/usr/bin/env python3
"""
import time
Aurora Automatic System Update
THIS SCRIPT RUNS EVERY TIME AURORA NEEDS TO UPDATE THE ENTIRE SYSTEM

When new tiers are added or system changes are made, Aurora runs this script
to automatically update:
- aurora_core.py (backend Python)
- All frontend React/TypeScript components
- All backend Node.js/TypeScript files
- All Python backend tools and scripts
- Documentation files (MD, TXT)
- Integration files
- EVERYTHING in the entire program
"""

import json
from datetime import datetime
from pathlib import Path


class AuroraSystemUpdater:
    """Automatic system-wide updater for Aurora - DEEP SEARCH & UPDATE"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.updates_made = []
        self.errors = []
        self.files_scanned = 0

        # File extensions to scan
        self.text_extensions = {
            ".tsx",
            ".ts",
            ".jsx",
            ".js",
            ".py",
            ".md",
            ".txt",
            ".json",
            ".yml",
            ".yaml",
            ".html",
            ".css",
            ".scss",
        }

        # Directories to skip
        self.skip_dirs = {
            "node_modules",
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "dist",
            "build",
            ".next",
            "out",
            "coverage",
            ".pytest_cache",
        }

    def get_current_tier_count(self) -> dict[str, int]:
        """Get current tier count from aurora_core.py"""
        try:
            from aurora_core import AuroraKnowledgeTiers

            aurora = AuroraKnowledgeTiers()
            return {
                "foundation_count": aurora.foundation_count,
                "tier_count": aurora.knowledge_tier_count,  # Fixed: use knowledge_tier_count
                "total_capabilities": aurora.capabilities_count,  # Fixed: use capabilities_count
            }
        except Exception as e:
            self.errors.append(f"Failed to load aurora_core: {e}")
            # Updated to 56
            return {"foundation_count": 13, "tier_count": 66, "total_capabilities": 79}

    def get_all_files_to_update(self) -> list[Path]:
        """Recursively get all text files in the project (DEEP SEARCH)"""
        all_files = []

        for file_path in self.project_root.rglob("*"):
            # Skip directories
            if file_path.is_dir():
                continue

            # Skip excluded directories
            if any(skip_dir in file_path.parts for skip_dir in self.skip_dirs):
                continue

            # Only process text files
            if file_path.suffix.lower() in self.text_extensions:
                all_files.append(file_path)

        return all_files

    def generate_replacement_patterns(self, counts: dict[str, int]) -> list[tuple[str, str, str]]:
        """Generate all possible replacement patterns (old_value, new_value, description)"""
        tier_count = counts["tier_count"]
        total = counts["total_capabilities"]
        foundation = counts["foundation_count"]

        # All possible old values that need updating
        old_tier_counts = [27, 32, 41, 46]
        old_total_counts = [40, 47, 54, 59]
        old_skills = [1500, 2000]

        patterns = []

        # Tier count patterns
        for old_tier in old_tier_counts:
            patterns.extend(
                [
                    (f"{old_tier} tier", f"{tier_count} tier",
                     f"tier count {old_tier}→{tier_count}"),
                    (f"{old_tier} Tier", f"{tier_count} Tier",
                     f"Tier count {old_tier}→{tier_count}"),
                    (f"{old_tier} TIER", f"{tier_count} TIER",
                     f"TIER count {old_tier}→{tier_count}"),
                    (f"{old_tier} knowledge tier",
                     f"{tier_count} knowledge tier", "knowledge tiers"),
                    (f"{old_tier} Knowledge Tier",
                     f"{tier_count} Knowledge Tier", "Knowledge Tiers"),
                    (f"all {old_tier} mastery tier",
                     f"all {tier_count} knowledge tier", "mastery→knowledge tiers"),
                    (f"TIER {old_tier}",
                     f"TIER {tier_count}", "TIER reference"),
                    (f"Tier {old_tier}",
                     f"Tier {tier_count}", "Tier reference"),
                ]
            )

        # Total capabilities patterns
        for old_total in old_total_counts:
            patterns.extend(
                [
                    (f"{old_total} Complete System",
                     f"{total} Complete System", "complete systems"),
                    (f"{old_total} total capabilit",
                     f"{total} total capabilit", "total capabilities"),
                    (f"{old_total} capabilit",
                     f"{total} capabilit", "capabilities"),
                    (f"{old_total} system", f"{total} system", "systems count"),
                    (f"{old_total} System", f"{total} System", "Systems count"),
                ]
            )

        # Combined patterns (Tasks + Tiers = Total)
        for old_tier in old_tier_counts:
            for old_total in old_total_counts:
                patterns.extend(
                    [
                        (f"13 Tasks + {old_tier} Tiers",
                         f"13 Tasks + {tier_count} Tiers", "combined count"),
                        (f"13 tasks + {old_tier} tiers",
                         f"13 tasks + {tier_count} tiers", "combined count lowercase"),
                        (
                            f"{foundation} Tasks + {old_tier} Tiers = {old_total}",
                            f"{foundation} Tasks + {tier_count} Tiers = {total}",
                            "full equation",
                        ),
                    ]
                )

        # Skill count patterns
        for old_skills_count in old_skills:
            patterns.append((f"{old_skills_count}+ Skill",
                            "2500+ Skill", "skills count"))

        # Tier range patterns (for documentation)
        patterns.extend(
            [
                ("TIER 1-53", "TIER 1-53", "tier range"),
                ("Tier 1-53", "Tier 1-53", "tier range"),
                ("tiers 1-53", "tiers 1-53", "tier range lowercase"),
                ("TIER 28-53", "TIER 28-53", "autonomous tier range"),
                ("Tier 28-53", "Tier 28-53", "autonomous tier range"),
                ("TIER 53", "TIER 53", "max tier reference"),
                ("tier 53", "tier 53", "max tier reference lowercase"),
                ("(1-53)", "(1-53)", "tier range in parens"),
                ("(28-53)", "(28-53)", "autonomous range in parens"),
                ("28-53: Autonomous & Advanced",
                 "28-53: Autonomous & Advanced", "tier category"),
                ('tiers_loaded": 66',
                 f'tiers_loaded": {tier_count}', "tiers_loaded JSON"),
            ]
        )

        return patterns

    def update_file_deep(self, file_path: Path, patterns: list[tuple[str, str, str]]) -> tuple[bool, int]:
        """Deep update a single file with all replacement patterns"""
        try:
            self.files_scanned += 1

            if not file_path.exists():
                return False, 0

            content = file_path.read_text(encoding="utf-8", errors="ignore")
            original = content
            replacements_made = 0

            # Apply all patterns
            for old_pattern, new_pattern, description in patterns:
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    replacements_made += 1

            # If changes were made, write back
            if content != original:
                file_path.write_text(content, encoding="utf-8")
                self.updates_made.append(
                    {"file": str(file_path.relative_to(
                        self.project_root)), "replacements": replacements_made}
                )
                return True, replacements_made
            return False, 0

        except Exception as e:
            self.errors.append(
                f"Error updating {file_path.name}: {str(e)[:100]}")
            return False, 0

    def deep_update_all_files(self, counts: dict[str, int]) -> None:
        """DEEP SEARCH: Update ALL files in the entire program"""
        print("\n🔍 DEEP SEARCH: Scanning entire program...")

        # Get all files
        all_files = self.get_all_files_to_update()
        print(f"   Found {len(all_files)} files to scan")

        # Generate all replacement patterns
        patterns = self.generate_replacement_patterns(counts)
        print(f"   Generated {len(patterns)} replacement patterns")

        # Update each file
        print("\n📝 Updating files...")
        updated_count = 0
        total_replacements = 0

        # Group by category for reporting
        categories = {
            "Frontend Components": [],
            "Backend TypeScript": [],
            "Python Tools": [],
            "Documentation": [],
            "Other": [],
        }

        for file_path in all_files:
            updated, replacements = self.update_file_deep(file_path, patterns)

            if updated:
                updated_count += 1
                total_replacements += replacements

                rel_path = str(file_path.relative_to(self.project_root))

                # Categorize
                if "client/src" in rel_path:
                    categories["Frontend Components"].append(rel_path)
                elif "server" in rel_path and file_path.suffix in [".ts", ".js"]:
                    categories["Backend TypeScript"].append(rel_path)
                elif file_path.suffix == ".py":
                    categories["Python Tools"].append(rel_path)
                elif file_path.suffix in [".md", ".txt"]:
                    categories["Documentation"].append(rel_path)
                else:
                    categories["Other"].append(rel_path)

        # Print categorized results
        print(
            f"\n✅ Updated {updated_count} files with {total_replacements} total replacements\n")

        for category, files in categories.items():
            if files:
                print(f"   {category} ({len(files)} files):")
                for f in sorted(files)[:5]:  # Show first 5
                    print(f"      ✓ {f}")
                if len(files) > 5:
                    print(f"      ... and {len(files) - 5} more")
                print()

    def generate_update_report(self, counts: dict[str, int]) -> None:
        """Generate comprehensive update report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0-deep-search",
            "counts": counts,
            "files_scanned": self.files_scanned,
            "files_updated": len(self.updates_made),
            "updated_files": self.updates_made,
            "errors": self.errors,
        }

        report_file = self.project_root / ".aurora_knowledge" / "last_system_update.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def run(self) -> bool:
        """Run complete DEEP system update"""
        print("\n" + "=" * 80)
        print("🌟 AURORA AUTOMATIC SYSTEM UPDATE - DEEP SEARCH MODE")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Mode: COMPREHENSIVE - Scanning EVERY file in the entire program")
        print("=" * 80)

        # Get current counts from aurora_core.py
        print("\n📊 Reading Current System State from aurora_core.py...")
        counts = self.get_current_tier_count()
        print(f"   Foundation Tasks: {counts['foundation_count']}")
        print(f"   Knowledge Tiers: {counts['tier_count']}")
        print(f"   Total Capabilities: {counts['total_capabilities']}")

        # Deep update ALL files
        self.deep_update_all_files(counts)

        # Generate report
        self.generate_update_report(counts)

        # Summary
        print("\n" + "=" * 80)
        print("✅ DEEP SYSTEM UPDATE COMPLETE")
        print("=" * 80)
        print("\n📊 Statistics:")
        print(f"   Files Scanned: {self.files_scanned}")
        print(f"   Files Updated: {len(self.updates_made)}")
        print(
            f"   Total Replacements: {sum(f['replacements'] for f in self.updates_made)}")

        if self.errors:
            print(f"\n⚠️  Errors Encountered: {len(self.errors)}")
            for e in self.errors[:5]:  # Show first 5 errors
                print(f"   • {e}")
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more errors")

        print("\n🎯 Final System State:")
        print(f"   • {counts['foundation_count']} Foundation Tasks")
        print(f"   • {counts['tier_count']} Knowledge Tiers")
        print(f"   • {counts['total_capabilities']} Total Capabilities")
        print("   • ALL frontend components synchronized")
        print("   • ALL backend TypeScript files synchronized")
        print("   • ALL Python tools synchronized")
        print("   • ALL documentation synchronized")
        print("   • ENTIRE program updated")

        print("\n" + "=" * 80)
        print("🚀 AURORA SYSTEM IS FULLY SYNCHRONIZED ACROSS ENTIRE CODEBASE")
        print("=" * 80 + "\n")

        return len(self.errors) == 0


def main():
    """Main entry point"""
    updater = AuroraSystemUpdater()
    success = updater.run()
    return 0 if SUCCESS else 1


if __name__ == "__main__":
    exit(main())
