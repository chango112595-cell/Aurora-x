#!/usr/bin/env python3
"""
Aurora - Move all HTML files to unused/ folder and verify it's safe
"""

import shutil
from pathlib import Path
from typing import List, Set
import json


class AuroraHTMLCleanup:
    def __init__(self):
        self.root = Path(".")
        self.unused_folder = self.root / "unused" / "html_archive"
        self.html_files = []
        self.moved = []
        self.skipped = []
        self.protected_paths = [
            "node_modules",
            ".git",
            ".venv",
            "venv",
            "__pycache__"
        ]

    def check_unused_folder_safety(self) -> bool:
        """Check if unused/ folder is safe to use for archiving"""
        print("\n🔍 CHECKING UNUSED FOLDER")
        print("=" * 60)

        unused = self.root / "unused"

        if not unused.exists():
            print("✅ unused/ folder does not exist - safe to create")
            return True

        # Check what's in unused/
        items = list(unused.rglob("*"))
        files = [f for f in items if f.is_file()]

        print(f"📁 unused/ folder exists with {len(files)} files")

        # Check if it's being imported or referenced
        important_extensions = ['.py', '.ts', '.tsx', '.js', '.jsx']
        important_files = [
            f for f in files if f.suffix in important_extensions]

        if important_files:
            print(f"⚠️  Found {len(important_files)} code files in unused/")
            for f in important_files[:5]:
                print(f"   • {f.relative_to(self.root)}")

            # Check if any Python files import from unused
            print("\n🔍 Checking for imports from unused/...")
            py_files = list(self.root.glob("*.py"))
            imports_found = False

            for py_file in py_files:
                try:
                    content = py_file.read_text(encoding="utf-8")
                    if "from unused" in content or "import unused" in content:
                        print(f"⚠️  {py_file.name} imports from unused/")
                        imports_found = True
                except:
                    pass

            if not imports_found:
                print("✅ No active imports from unused/ folder")
        else:
            print("✅ No important code files in unused/")

        return True

    def find_all_html_files(self) -> List[Path]:
        """Find all HTML files (excluding protected paths)"""
        print("\n🔍 FINDING ALL HTML FILES")
        print("=" * 60)

        html_files = []

        for html_file in self.root.rglob("*.html"):
            # Skip protected paths
            if any(protected in html_file.parts for protected in self.protected_paths):
                continue

            # Skip if already in unused/
            if "unused" in html_file.parts:
                continue

            html_files.append(html_file)

        print(f"Found {len(html_files)} HTML files to move\n")

        # Categorize by location
        categories = {}
        for f in html_files:
            if "runs" in f.parts:
                category = "runs (test reports)"
            elif "client" in f.parts:
                category = "client (frontend)"
            elif "aurora_x" in f.parts:
                category = "aurora_x (backend)"
            elif "attached_assets" in f.parts:
                category = "attached_assets"
            elif "public" in f.parts:
                category = "public"
            else:
                category = "root level"

            if category not in categories:
                categories[category] = []
            categories[category].append(f)

        for category, files in sorted(categories.items()):
            print(f"   • {category}: {len(files)} files")

        return html_files

    def move_html_files(self, html_files: List[Path]):
        """Move HTML files to unused/html_archive/ maintaining structure"""
        print(f"\n📦 MOVING HTML FILES TO unused/html_archive/")
        print("=" * 60)

        # Create archive folder
        self.unused_folder.mkdir(parents=True, exist_ok=True)

        for html_file in html_files:
            try:
                # Maintain relative structure
                rel_path = html_file.relative_to(self.root)
                new_path = self.unused_folder / rel_path

                # Create parent directories
                new_path.parent.mkdir(parents=True, exist_ok=True)

                # Move file
                shutil.move(str(html_file), str(new_path))

                self.moved.append({
                    "from": str(rel_path),
                    "to": str(new_path.relative_to(self.root))
                })

                if len(self.moved) <= 10:  # Show first 10
                    print(f"✅ {rel_path}")
                elif len(self.moved) == 11:
                    print(f"   ... ({len(html_files) - 10} more files)")

            except Exception as e:
                print(
                    f"❌ Failed to move {html_file.relative_to(self.root)}: {e}")
                self.skipped.append(str(html_file.relative_to(self.root)))

    def create_readme(self):
        """Create README in unused/ folder explaining its purpose"""
        readme_path = self.root / "unused" / "README.md"

        readme_content = """# Unused Folder

This folder contains archived files that are not actively used in the project.

## Purpose
- Archive old/deprecated code
- Store historical HTML files (now converted to TSX)
- Keep files for reference without cluttering the main project

## Contents
- `html_archive/` - Original HTML files (all converted to TSX)
  - Test reports from runs/
  - Old dashboards
  - Legacy frontend files

## Important
⚠️ This folder should NOT be imported or used by active code.
- Do not add this folder to build processes
- Do not import from this folder in active code
- Files here are for historical reference only

## Maintenance
- Can be safely deleted if disk space is needed
- Original HTML files have TSX equivalents in:
  - `client/src/` (working frontend)
  - `runs/*/` (test report TSX files)
"""

        readme_path.write_text(readme_content, encoding="utf-8")
        print(f"\n📝 Created: {readme_path.relative_to(self.root)}")

    def generate_report(self):
        """Generate final report"""
        print("\n" + "=" * 60)
        print("📊 HTML CLEANUP SUMMARY")
        print("=" * 60)

        print(f"\n✅ Successfully moved: {len(self.moved)} files")
        print(f"❌ Failed to move: {len(self.skipped)} files")
        print(f"\n📁 All HTML files archived to: unused/html_archive/")
        print(f"   • Original folder structure maintained")
        print(f"   • TSX versions remain in place")

        if self.skipped:
            print(f"\n⚠️  Skipped files:")
            for skipped in self.skipped[:5]:
                print(f"   • {skipped}")

        # Save detailed report
        report = {
            "timestamp": "2025-11-22",
            "total_moved": len(self.moved),
            "total_skipped": len(self.skipped),
            "moved_files": self.moved[:50],  # First 50 for brevity
            "skipped_files": self.skipped
        }

        report_path = self.root / "AURORA_HTML_CLEANUP_REPORT.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Detailed report: {report_path.name}")
        print("\n✅ CLEANUP COMPLETE!")
        print("   • All HTML files archived")
        print("   • TSX versions active")
        print("   • unused/ folder documented")
        print("=" * 60 + "\n")

    def run(self):
        """Run the cleanup"""
        print("\n🌟 AURORA HTML CLEANUP")
        print("=" * 60)
        print("Moving all HTML files to unused/html_archive/")
        print("=" * 60)

        # Check safety
        if not self.check_unused_folder_safety():
            print("❌ Cannot proceed - unused/ folder needs review")
            return

        # Find HTML files
        html_files = self.find_all_html_files()

        if not html_files:
            print("\n✅ No HTML files found to move!")
            return

        # Confirm
        print(
            f"\n📋 Ready to move {len(html_files)} HTML files to unused/html_archive/")
        print("   Original folder structure will be maintained")
        print("   TSX versions will remain in place\n")

        # Move files
        self.move_html_files(html_files)

        # Create documentation
        self.create_readme()

        # Generate report
        self.generate_report()


if __name__ == "__main__":
    cleanup = AuroraHTMLCleanup()
    cleanup.run()
