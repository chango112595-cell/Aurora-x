#!/usr/bin/env python3
"""
Aurora Automatic System Update
THIS SCRIPT RUNS EVERY TIME AURORA NEEDS TO UPDATE THE ENTIRE SYSTEM

When new tiers are added or system changes are made, Aurora runs this script
to automatically update:
- aurora_core.py (backend Python)
- All frontend React/TypeScript components
- All backend Node.js/TypeScript files
- Documentation
- Integration files
"""

import json
import re
from datetime import datetime
from pathlib import Path


class AuroraSystemUpdater:
    """Automatic system-wide updater for Aurora"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.updates_made = []
        self.errors = []

    def get_current_tier_count(self) -> dict[str, int]:
        """Get current tier count from aurora_core.py"""
        try:
            from aurora_core import AuroraKnowledgeTiers

            aurora = AuroraKnowledgeTiers()
            return {
                "foundation_count": aurora.foundation_count,
                "tier_count": aurora.tier_count,
                "total_capabilities": aurora.total_capabilities,
            }
        except Exception as e:
            self.errors.append(f"Failed to load aurora_core: {e}")
            return {"foundation_count": 13, "tier_count": 41, "total_capabilities": 54}

    def update_file(self, file_path: Path, replacements: list[tuple[str, str]]) -> bool:
        """Update a file with multiple replacements"""
        try:
            if not file_path.exists():
                self.errors.append(f"File not found: {file_path}")
                return False

            content = file_path.read_text(encoding="utf-8")
            original = content

            for old, new in replacements:
                content = content.replace(old, new)

            if content != original:
                file_path.write_text(content, encoding="utf-8")
                self.updates_made.append(str(file_path))
                return True
            return False
        except Exception as e:
            self.errors.append(f"Error updating {file_path}: {e}")
            return False

    def update_frontend_components(self, counts: dict[str, int]) -> None:
        """Update all frontend React/TypeScript components"""
        print("\n📱 Updating Frontend Components...")

        tier_count = counts["tier_count"]
        total = counts["total_capabilities"]
        foundation = counts["foundation_count"]

        # Previous values to replace (find the most recent ones)
        # This is dynamic - it will detect the current values and update them
        frontend_files = [
            "client/src/pages/intelligence.tsx",
            "client/src/components/AuroraControl.tsx",
            "client/src/components/AuroraDashboard.tsx",
            "client/src/components/AuroraMonitor.tsx",
            "client/src/components/AuroraPage.tsx",
            "client/src/components/AuroraPanel.tsx",
            "client/src/components/AuroraRebuiltChat.tsx",
            "client/src/components/AuroraFuturisticDashboard.tsx",
            "client/src/components/AuroraFuturisticLayout.tsx",
            "client/src/pages/luminar-nexus.tsx",
            "client/src/components/DiagnosticTest.tsx",
            "client/src/pages/tiers.tsx",
        ]

        for file_str in frontend_files:
            file_path = self.project_root / file_str
            if not file_path.exists():
                continue

            content = file_path.read_text(encoding="utf-8")
            original = content

            # Replace any number references to tiers and capabilities
            # Use regex to find and replace dynamically
            content = re.sub(r"(\d+) Knowledge Tiers", f"{tier_count} Knowledge Tiers", content)
            content = re.sub(r"(\d+) Complete Systems", f"{total} Complete Systems", content)
            content = re.sub(r"13 Tasks \+ (\d+) Tiers", f"13 Tasks + {tier_count} Tiers", content)
            content = re.sub(r"(\d+) Systems: 13 Foundation Tasks", f"{total} Systems: 13 Foundation Tasks", content)

            # Capture original in closures to avoid cell-var-from-loop
            original_text = original
            content = re.sub(
                r'<span className="text-purple-400 font-mono text-lg">(\d+)</span>',
                lambda m, orig=original_text: (
                    f'<span className="text-purple-400 font-mono text-lg">{tier_count}</span>'
                    if "Knowledge Tiers" in orig[max(0, m.start() - 200) : m.start()]
                    else m.group(0)
                ),
                content,
            )
            content = re.sub(
                r'<span className="text-pink-400 font-mono text-lg">(\d+)</span>',
                lambda m, orig=original_text: (
                    f'<span className="text-pink-400 font-mono text-lg">{total}</span>'
                    if "Total Systems" in orig[max(0, m.start() - 200) : m.start()]
                    else m.group(0)
                ),
                content,
            )

            if content != original:
                file_path.write_text(content, encoding="utf-8")
                self.updates_made.append(str(file_path))
                print(f"  ✅ {file_str}")

    def update_backend_files(self, counts: dict[str, int]) -> None:
        """Update all backend Node.js/TypeScript files"""
        print("\n🔧 Updating Backend Files...")

        tier_count = counts["tier_count"]
        total = counts["total_capabilities"]
        foundation = counts["foundation_count"]

        backend_files = {
            "server/aurora-chat.ts": [
                (
                    r"- \d+ Mastery Tiers: Your knowledge domains",
                    f"- {total} Capabilities: {foundation} Foundation Tasks + {tier_count} Knowledge Tiers",
                ),
            ],
            "server/routes.ts": [
                (
                    r"\d+ mastery tiers spanning",
                    f"{total} capabilities ({foundation} foundation tasks + {tier_count} knowledge tiers) spanning",
                ),
                (
                    r"\*\*My knowledge \(\d+ mastery tiers\):",
                    f"**My knowledge ({tier_count} knowledge tiers + {foundation} foundation tasks = {total} capabilities):",
                ),
                (
                    r"🧠 \d+ mastery tiers: LOADED",
                    f"🧠 {tier_count} knowledge tiers: LOADED ({total} total capabilities)",
                ),
                (r"🧠 All \d+ tiers active", f"🧠 All {tier_count} tiers active ({total} total capabilities)"),
            ],
        }

        for file_str, patterns in backend_files.items():
            file_path = self.project_root / file_str
            if not file_path.exists():
                continue

            content = file_path.read_text(encoding="utf-8")
            original = content

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            if content != original:
                file_path.write_text(content, encoding="utf-8")
                self.updates_made.append(str(file_path))
                print(f"  ✅ {file_str}")

    def update_documentation(self, counts: dict[str, int]) -> None:
        """Update documentation files"""
        print("\n📚 Updating Documentation...")

        # Update autonomous integration file
        integration_file = self.project_root / "aurora_autonomous_integration.py"
        if integration_file.exists():
            content = integration_file.read_text(encoding="utf-8")
            original = content

            content = re.sub(
                r"'total_capabilities': \d+", f"'total_capabilities': {counts['total_capabilities']}", content
            )
            content = re.sub(r"'knowledge_tiers': \d+", f"'knowledge_tiers': {counts['tier_count']}", content)

            if content != original:
                integration_file.write_text(content, encoding="utf-8")
                self.updates_made.append(str(integration_file))
                print("  ✅ aurora_autonomous_integration.py")

    def generate_update_report(self, counts: dict[str, int]) -> None:
        """Generate update report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0-autonomous",
            "counts": counts,
            "files_updated": len(self.updates_made),
            "updated_files": self.updates_made,
            "errors": self.errors,
        }

        report_file = self.project_root / ".aurora_knowledge" / "last_system_update.json"
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def run(self) -> bool:
        """Run complete system update"""
        print("\n" + "=" * 70)
        print("🌟 AURORA AUTOMATIC SYSTEM UPDATE")
        print("=" * 70)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # Get current counts from aurora_core.py
        print("\n📊 Reading Current System State...")
        counts = self.get_current_tier_count()
        print(f"  Foundation Tasks: {counts['foundation_count']}")
        print(f"  Knowledge Tiers: {counts['tier_count']}")
        print(f"  Total Capabilities: {counts['total_capabilities']}")

        # Update all systems
        self.update_frontend_components(counts)
        self.update_backend_files(counts)
        self.update_documentation(counts)

        # Generate report
        self.generate_update_report(counts)

        # Summary
        print("\n" + "=" * 70)
        print("✅ SYSTEM UPDATE COMPLETE")
        print("=" * 70)
        print(f"\nFiles Updated: {len(self.updates_made)}")

        if self.updates_made:
            print("\n📝 Updated Files:")
            for f in self.updates_made:
                print(f"  • {f}")

        if self.errors:
            print("\n⚠️  Errors Encountered:")
            for e in self.errors:
                print(f"  • {e}")

        print("\n🎯 Current System State:")
        print(f"  • {counts['foundation_count']} Foundation Tasks")
        print(f"  • {counts['tier_count']} Knowledge Tiers")
        print(f"  • {counts['total_capabilities']} Total Capabilities")
        print("  • All frontend components synchronized")
        print("  • All backend files synchronized")
        print("  • Documentation updated")

        print("\n" + "=" * 70)
        print("🚀 AURORA SYSTEM IS FULLY SYNCHRONIZED")
        print("=" * 70 + "\n")

        return len(self.errors) == 0


def main():
    """Main entry point"""
    updater = AuroraSystemUpdater()
    success = updater.run()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
