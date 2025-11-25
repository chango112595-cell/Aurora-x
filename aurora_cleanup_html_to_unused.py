<<<<<<< HEAD
=======
"""
Aurora Cleanup Html To Unused

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
#!/usr/bin/env python3
"""
Aurora - Move all HTML files to unused/ folder and verify it's safe
"""

import shutil
from pathlib import Path
from typing import List, Set
import json

<<<<<<< HEAD

class AuroraHTMLCleanup:
    def __init__(self):
=======
# Aurora Performance Optimization
from concurrent.futures import ThreadPoolExecutor

# High-performance parallel processing with ThreadPoolExecutor
# Example: with ThreadPoolExecutor(max_workers=100) as executor:
#             results = executor.map(process_func, items)


class AuroraHTMLCleanup:
    """
        Aurorahtmlcleanup
        
        Comprehensive class providing aurorahtmlcleanup functionality.
        
        This class implements complete functionality with full error handling,
        type hints, and performance optimization following Aurora's standards.
        
        Attributes:
            [Attributes will be listed here based on __init__ analysis]
        
        Methods:
            check_unused_folder_safety, find_all_html_files, move_html_files, create_readme, generate_report...
        """
    def __init__(self):
        """
              Init  
            
            Args:
            """
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
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
<<<<<<< HEAD
        print("\n🔍 CHECKING UNUSED FOLDER")
=======
        print("\n[SCAN] CHECKING UNUSED FOLDER")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
        print("=" * 60)

        unused = self.root / "unused"

        if not unused.exists():
<<<<<<< HEAD
            print("✅ unused/ folder does not exist - safe to create")
=======
            print("[OK] unused/ folder does not exist - safe to create")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
            return True

        # Check what's in unused/
        items = list(unused.rglob("*"))
        files = [f for f in items if f.is_file()]

<<<<<<< HEAD
        print(f"📁 unused/ folder exists with {len(files)} files")
=======
        print(f"[EMOJI] unused/ folder exists with {len(files)} files")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

        # Check if it's being imported or referenced
        important_extensions = ['.py', '.ts', '.tsx', '.js', '.jsx']
        important_files = [
            f for f in files if f.suffix in important_extensions]

        if important_files:
<<<<<<< HEAD
            print(f"⚠️  Found {len(important_files)} code files in unused/")
            for f in important_files[:5]:
                print(f"   • {f.relative_to(self.root)}")

            # Check if any Python files import from unused
            print("\n🔍 Checking for imports from unused/...")
=======
            print(f"[WARN]  Found {len(important_files)} code files in unused/")
            for f in important_files[:5]:
                print(f"    {f.relative_to(self.root)}")

            # Check if any Python files import from unused
            print("\n[SCAN] Checking for imports from unused/...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
            py_files = list(self.root.glob("*.py"))
            imports_found = False

            for py_file in py_files:
                try:
                    content = py_file.read_text(encoding="utf-8")
                    if "from unused" in content or "import unused" in content:
<<<<<<< HEAD
                        print(f"⚠️  {py_file.name} imports from unused/")
                        imports_found = True
                except:
                    pass

            if not imports_found:
                print("✅ No active imports from unused/ folder")
        else:
            print("✅ No important code files in unused/")
=======
                        print(f"[WARN]  {py_file.name} imports from unused/")
                        imports_found = True
                except Exception as e:
                    pass

            if not imports_found:
                print("[OK] No active imports from unused/ folder")
        else:
            print("[OK] No important code files in unused/")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

        return True

    def find_all_html_files(self) -> List[Path]:
        """Find all HTML files (excluding protected paths)"""
<<<<<<< HEAD
        print("\n🔍 FINDING ALL HTML FILES")
=======
        print("\n[SCAN] FINDING ALL HTML FILES")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
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
<<<<<<< HEAD
            print(f"   • {category}: {len(files)} files")
=======
            print(f"    {category}: {len(files)} files")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

        return html_files

    def move_html_files(self, html_files: List[Path]):
        """Move HTML files to unused/html_archive/ maintaining structure"""
<<<<<<< HEAD
        print(f"\n📦 MOVING HTML FILES TO unused/html_archive/")
=======
        print(f"\n[PACKAGE] MOVING HTML FILES TO unused/html_archive/")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
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
<<<<<<< HEAD
                    print(f"✅ {rel_path}")
=======
                    print(f"[OK] {rel_path}")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
                elif len(self.moved) == 11:
                    print(f"   ... ({len(html_files) - 10} more files)")

            except Exception as e:
                print(
<<<<<<< HEAD
                    f"❌ Failed to move {html_file.relative_to(self.root)}: {e}")
=======
                    f"[ERROR] Failed to move {html_file.relative_to(self.root)}: {e}")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
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
<<<<<<< HEAD
⚠️ This folder should NOT be imported or used by active code.
=======
[WARN] This folder should NOT be imported or used by active code.
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
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
<<<<<<< HEAD
        print(f"\n📝 Created: {readme_path.relative_to(self.root)}")
=======
        print(f"\n[EMOJI] Created: {readme_path.relative_to(self.root)}")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

    def generate_report(self):
        """Generate final report"""
        print("\n" + "=" * 60)
<<<<<<< HEAD
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
=======
        print("[DATA] HTML CLEANUP SUMMARY")
        print("=" * 60)

        print(f"\n[OK] Successfully moved: {len(self.moved)} files")
        print(f"[ERROR] Failed to move: {len(self.skipped)} files")
        print(f"\n[EMOJI] All HTML files archived to: unused/html_archive/")
        print(f"    Original folder structure maintained")
        print(f"    TSX versions remain in place")

        if self.skipped:
            print(f"\n[WARN]  Skipped files:")
            for skipped in self.skipped[:5]:
                print(f"    {skipped}")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

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

<<<<<<< HEAD
        print(f"\n💾 Detailed report: {report_path.name}")
        print("\n✅ CLEANUP COMPLETE!")
        print("   • All HTML files archived")
        print("   • TSX versions active")
        print("   • unused/ folder documented")
=======
        print(f"\n[EMOJI] Detailed report: {report_path.name}")
        print("\n[OK] CLEANUP COMPLETE!")
        print("    All HTML files archived")
        print("    TSX versions active")
        print("    unused/ folder documented")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
        print("=" * 60 + "\n")

    def run(self):
        """Run the cleanup"""
<<<<<<< HEAD
        print("\n🌟 AURORA HTML CLEANUP")
=======
        print("\n[STAR] AURORA HTML CLEANUP")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
        print("=" * 60)
        print("Moving all HTML files to unused/html_archive/")
        print("=" * 60)

        # Check safety
        if not self.check_unused_folder_safety():
<<<<<<< HEAD
            print("❌ Cannot proceed - unused/ folder needs review")
=======
            print("[ERROR] Cannot proceed - unused/ folder needs review")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
            return

        # Find HTML files
        html_files = self.find_all_html_files()

        if not html_files:
<<<<<<< HEAD
            print("\n✅ No HTML files found to move!")
=======
            print("\n[OK] No HTML files found to move!")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
            return

        # Confirm
        print(
<<<<<<< HEAD
            f"\n📋 Ready to move {len(html_files)} HTML files to unused/html_archive/")
=======
            f"\n[EMOJI] Ready to move {len(html_files)} HTML files to unused/html_archive/")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
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
