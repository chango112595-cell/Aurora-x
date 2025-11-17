#!/usr/bin/env python3
"""
Aurora Focused Project Fixer - Only fix root-level Python files
Excludes virtual environments, node_modules, and library code
"""

import re
import subprocess
from pathlib import Path


class AuroraFocusedFixer:
    """Aurora's focused fixer for project files only"""

    def __init__(self):
        self.root = Path.cwd()
        self.fixes_applied = 0
        self.files_modified = set()

        # Only target root-level .py files (YOUR code)
        self.target_files = [f for f in self.root.glob("*.py") if f.is_file() and not f.name.startswith(".")]

    def run_fixes(self):
        """Run targeted fixes on project files only"""
        print("🎯 Aurora Focused Fixer - Project Files Only")
        print("=" * 80)
        print(f"Targeting {len(self.target_files)} root-level Python files\n")

        for filepath in self.target_files:
            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                original = content

                # Fix 1: Remove broken docstrings that were auto-added
                content = re.sub(r'(\s+)("""Class implementation"""\n)', r"", content)
                content = re.sub(r'(\s+)("""Function implementation"""\n)', r"", content)

                # Fix 2: Fix f-strings more carefully (only simple cases)
                # Only convert if there's definitely no interpolation
                lines = content.split("\n")
                new_lines = []
                for line in lines:
                    # Count braces to ensure no interpolation
                    if '"' in line or "'" in line:
                        open_braces = line.count("{")
                        close_braces = line.count("}")
                        # Only if NO braces at all
                        if open_braces == 0 and close_braces == 0:
                            line = re.sub(r'"([^"]*)"', r'"\1"', line)
                            line = re.sub(r"'([^']*)'", r"'\1'", line)
                    new_lines.append(line)
                content = "\n".join(new_lines)

                # Write back if changed
                if content != original:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.fixes_applied += 1
                    self.files_modified.add(str(filepath))
                    print(f"✅ Fixed: {filepath.name}")

            except Exception as e:
                print(f"⚠️  Error with {filepath.name}: {e}")

        print(f"\n✨ Applied {self.fixes_applied} fixes to {len(self.files_modified)} files")


def main():
    """Main execution"""
    fixer = AuroraFocusedFixer()
    fixer.run_fixes()

    print("\n🔍 Running pylint verification...")
    result = subprocess.run(
        ["python", "-m", "pylint", "*.py", "--disable=C,R", "--max-line-length=120"],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    for line in result.stdout.split("\n"):
        if "rated at" in line:
            print(f"   {line}")

    return 0


if __name__ == "__main__":
    exit(main())
