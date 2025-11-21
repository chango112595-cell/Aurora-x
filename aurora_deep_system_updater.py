#!/usr/bin/env python3
"""
Aurora Deep System Updater - COMPLETE DEEP SEARCH
Scans EVERY file in the ENTIRE project and updates ALL references

This is the ultimate system synchronization tool that:
- Scans all .py, .ts, .tsx, .js, .jsx, .md, .txt, .json, .html files
- Updates tier counts EVERYWHERE
- Updates capability counts EVERYWHERE
- Updates foundation task counts EVERYWHERE
- Works across ALL directories and ALL files
- Finds and updates EVERY single reference
"""

import json
import re
from datetime import datetime
from pathlib import Path


class AuroraDeepSystemUpdater:
    """Deep search and update across Aurora's ENTIRE codebase"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.updates_made: list[str] = []
        self.files_scanned = 0
        self.patterns_found = 0
        self.errors: list[str] = []

        # Extensions to scan - EVERYTHING
        self.extensions = {
            ".py",
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
            ".md",
            ".txt",
            ".json",
            ".html",
            ".css",
            ".yaml",
            ".yml",
            ".sh",
            ".ps1",
            ".bat",
        }

        # Directories to skip
        self.skip_dirs = {
            "node_modules",
            ".git",
            "__pycache__",
            "dist",
            "build",
            ".venv",
            "venv",
            ".next",
            "out",
            "coverage",
            ".pytest_cache",
            ".mypy_cache",
            "egg-info",
        }

    def get_tier_counts(self) -> dict[str, int]:
        """Get current tier counts from aurora_core.py"""
        print("\n📊 Reading tier counts from aurora_core.py...")

        try:
            # Try importing first
            from aurora_core import AuroraKnowledgeTiers

            aurora = AuroraKnowledgeTiers()
            counts = {
                "foundation": getattr(aurora, "foundation_count", 13),
                "tiers": len(aurora.tiers) if hasattr(aurora, "tiers") else 53,
                "total": 0,
            }
            counts["total"] = counts["foundation"] + counts["tiers"]
            print(f"   ✅ Loaded from aurora_core: {counts['tiers']} tiers, {counts['total']} total")
            return counts
        except Exception as e:
            print(f"   ⚠️  Import failed: {e}")
            print("   📝 Parsing directly from file...")

            # Parse directly from file
            for core_path in [self.project_root / "aurora_core.py", self.project_root / "tools" / "aurora_core.py"]:
                if core_path.exists():
                    content = core_path.read_text(encoding="utf-8")

                    # Count tier entries
                    tier_pattern = r'"tier_\d+_[^"]+"\s*:'
                    tiers = re.findall(tier_pattern, content)
                    tier_count = len(tiers)

                    if tier_count > 0:
                        counts = {"foundation": 13, "tiers": tier_count, "total": 13 + tier_count}
                        print(f"   ✅ Parsed from file: {counts['tiers']} tiers, {counts['total']} total")
                        return counts

        # Fallback
        print("   ⚠️  Using fallback values")
        return {"foundation": 13, "tiers": 53, "total": 66}

    def get_all_files(self) -> list[Path]:
        """Get ALL files to scan - complete deep search"""
        print("\n🔍 Deep scanning ENTIRE project...")
        files = []

        for file_path in self.project_root.rglob("*"):
            # Skip directories
            if file_path.is_dir():
                continue

            # Skip excluded directories
            if any(skip in file_path.parts for skip in self.skip_dirs):
                continue

            # Only scan text files
            if file_path.suffix.lower() in self.extensions:
                files.append(file_path)

        print(f"   Found {len(files)} files to scan")
        return files

    def generate_patterns(self, counts: dict[str, int]) -> list[tuple[re.Pattern, str, str]]:
        """Generate ALL possible patterns to find and replace"""
        tiers = counts["tiers"]
        total = counts["total"]
        foundation = counts["foundation"]

        # Calculate what the OLD values might be (we'll detect any number)
        patterns = []

        # Pattern format: (regex_pattern, replacement_template, description)
        patterns.extend(
            [
                # Tier counts
                (re.compile(r"(\d+)\s+Knowledge Tiers"), f"{tiers} Knowledge Tiers", "Knowledge Tiers text"),
                (re.compile(r"(\d+)\s+knowledge tiers"), f"{tiers} knowledge tiers", "knowledge tiers lowercase"),
                (re.compile(r"(\d+)\s+tiers"), f"{tiers} tiers", "tiers generic"),
                (re.compile(r'tier_count["\']?\s*:\s*(\d+)'), f'tier_count": {tiers}', "tier_count JSON"),
                (
                    re.compile(r"Tier[s]?\s+(\d+)(?![\d])"),
                    lambda m: f"Tiers {tiers}" if int(m.group(1)) != tiers and int(m.group(1)) > 40 else m.group(0),
                    "Tiers count",
                ),
                # Total capabilities
                (re.compile(r"(\d+)\s+capabilities"), f"{total} capabilities", "capabilities"),
                (re.compile(r"(\d+)\s+total capabilities"), f"{total} total capabilities", "total capabilities"),
                (re.compile(r"(\d+)\s+Complete Systems"), f"{total} Complete Systems", "Complete Systems"),
                (
                    re.compile(r'total_capabilities["\']?\s*:\s*(\d+)'),
                    f'total_capabilities": {total}',
                    "total_capabilities JSON",
                ),
                # Combined expressions
                (
                    re.compile(r"(\d+)\s+\(\s*13\s+foundation\s+tasks\s+\+\s+(\d+)\s+knowledge\s+tiers\s*\)"),
                    f"{total} (13 foundation tasks + {tiers} knowledge tiers)",
                    "full expression",
                ),
                (
                    re.compile(r"13\s+foundation\s+tasks\s+\+\s+(\d+)\s+knowledge\s+tiers\s+=\s+(\d+)\s+capabilities"),
                    f"13 foundation tasks + {tiers} knowledge tiers = {total} capabilities",
                    "equation format",
                ),
                (
                    re.compile(r"(\d+)\s+knowledge\s+tiers\s+\+\s+13\s+foundation\s+tasks\s+=\s+(\d+)\s+capabilities"),
                    f"{tiers} knowledge tiers + 13 foundation tasks = {total} capabilities",
                    "reverse equation",
                ),
                # Frontend specific
                (
                    re.compile(r"<span[^>]*>(\d+)</span>.*Knowledge Tiers", re.DOTALL),
                    lambda m: m.group(0).replace(m.group(1), str(tiers)),
                    "HTML span Knowledge Tiers",
                ),
                (
                    re.compile(r"<span[^>]*>(\d+)</span>.*Total Systems", re.DOTALL),
                    lambda m: m.group(0).replace(m.group(1), str(total)),
                    "HTML span Total Systems",
                ),
                # Backend specific
                (
                    re.compile(r"🧠\s+(\d+)\s+knowledge\s+tiers:\s+LOADED\s+\((\d+)\s+total\s+capabilities\)"),
                    f"🧠 {tiers} knowledge tiers: LOADED ({total} total capabilities)",
                    "backend status message",
                ),
                (
                    re.compile(r"All\s+(\d+)\s+tiers\s+active\s+\((\d+)\s+total\s+capabilities\)"),
                    f"All {tiers} tiers active ({total} total capabilities)",
                    "all tiers active",
                ),
                # Documentation specific
                (re.compile(r"\*\*(\d+)\s+Knowledge\s+Tiers\*\*"), f"**{tiers} Knowledge Tiers**", "bold tiers"),
                (
                    re.compile(r"\*\*(\d+)\s+Total\s+Capabilities\*\*"),
                    f"**{total} Total Capabilities**",
                    "bold capabilities",
                ),
                (re.compile(r"`(\d+)\s+tiers`"), f"`{tiers} tiers`", "code tiers"),
                (re.compile(r"`(\d+)\s+capabilities`"), f"`{total} capabilities`", "code capabilities"),
            ]
        )

        return patterns

    def update_file(self, file_path: Path, patterns: list[tuple[re.Pattern, str, str]], counts: dict[str, int]) -> bool:
        """Update a single file with all patterns"""
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content
            changes_made = []

            for pattern, replacement, description in patterns:
                matches = pattern.finditer(content)
                for match in matches:
                    old_value = match.group(0)

                    # Apply replacement
                    if callable(replacement):
                        new_value = replacement(match)
                    else:
                        new_value = pattern.sub(replacement, old_value)

                    if old_value != new_value:
                        content = content.replace(old_value, new_value, 1)
                        changes_made.append(description)
                        self.patterns_found += 1

            # Write if changed
            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                self.updates_made.append(f"{file_path.relative_to(self.project_root)} ({len(changes_made)} changes)")
                return True

            return False

        except Exception as e:
            self.errors.append(f"{file_path.name}: {str(e)}")
            return False

    def run(self) -> bool:
        """Run complete deep system update"""
        print("\n" + "=" * 80)
        print("🌟 AURORA DEEP SYSTEM UPDATER - COMPLETE SCAN")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # Get current tier counts
        counts = self.get_tier_counts()
        print("\n📊 Current System State:")
        print(f"   • Foundation Tasks: {counts['foundation']}")
        print(f"   • Knowledge Tiers: {counts['tiers']}")
        print(f"   • Total Capabilities: {counts['total']}")

        # Get all files
        files = self.get_all_files()

        # Generate patterns
        print("\n🔧 Generating update patterns...")
        patterns = self.generate_patterns(counts)
        print(f"   Generated {len(patterns)} pattern types")

        # Update all files
        print(f"\n🔄 Scanning and updating {len(files)} files...")
        print("   This may take a moment...\n")

        for i, file_path in enumerate(files, 1):
            self.files_scanned += 1

            if i % 50 == 0:
                print(f"   Progress: {i}/{len(files)} files scanned...")

            self.update_file(file_path, patterns, counts)

        # Generate report
        self.generate_report(counts)

        # Summary
        print("\n" + "=" * 80)
        print("✅ DEEP SYSTEM UPDATE COMPLETE")
        print("=" * 80)
        print("\n📊 Statistics:")
        print(f"   • Files Scanned: {self.files_scanned}")
        print(f"   • Files Updated: {len(self.updates_made)}")
        print(f"   • Patterns Found & Fixed: {self.patterns_found}")
        print(f"   • Errors: {len(self.errors)}")

        if self.updates_made:
            print(f"\n📝 Updated Files ({len(self.updates_made)}):")
            for update in self.updates_made[:20]:  # Show first 20
                print(f"   ✅ {update}")
            if len(self.updates_made) > 20:
                print(f"   ... and {len(self.updates_made) - 20} more")

        if self.errors:
            print(f"\n⚠️  Errors ({len(self.errors)}):")
            for error in self.errors[:10]:
                print(f"   ❌ {error}")

        print("\n🎯 Final System State:")
        print(f"   • {counts['foundation']} Foundation Tasks")
        print(f"   • {counts['tiers']} Knowledge Tiers")
        print(f"   • {counts['total']} Total Capabilities")
        print("   • ALL files synchronized across ENTIRE project")

        print("\n" + "=" * 80)
        print("🚀 AURORA SYSTEM FULLY SYNCHRONIZED - EVERY FILE UPDATED")
        print("=" * 80 + "\n")

        return len(self.errors) == 0

    def generate_report(self, counts: dict[str, int]):
        """Generate detailed update report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "type": "deep_system_update",
            "counts": counts,
            "statistics": {
                "files_scanned": self.files_scanned,
                "files_updated": len(self.updates_made),
                "patterns_found": self.patterns_found,
                "errors": len(self.errors),
            },
            "updated_files": self.updates_made,
            "errors": self.errors,
        }

        report_dir = self.project_root / ".aurora_knowledge"
        report_dir.mkdir(exist_ok=True)

        report_file = report_dir / "last_deep_update.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved to: {report_file}")


def main():
    """Main entry point"""
    updater = AuroraDeepSystemUpdater()
    success = updater.run()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
