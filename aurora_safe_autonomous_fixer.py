#!/usr/bin/env python3
"""
Aurora Safe Autonomous Fixer - Learned from mistakes
Fixes only the syntax errors I created, with validation
"""

import ast
import re
import subprocess
from pathlib import Path


class AuroraSafeFixer:
    """Aurora's new smart fixer with validation - fixing my own mistakes"""

    def __init__(self):
        self.root = Path.cwd()
        self.fixes_applied = 0
        self.files_fixed = []
        self.files_failed = []

        # ONLY target root-level project files (not libraries!)
        self.target_files = [
            f
            for f in self.root.glob("*.py")
            if f.is_file() and not f.name.startswith(".") and ".venv" not in str(f) and "node_modules" not in str(f)
        ]

        print("🤖 Aurora Safe Fixer - Fixing My Mistakes")
        print("=" * 80)
        print("📋 I broke these files with my regex docstring removal")
        print("📋 Now I'll fix them properly using AST and validation")
        print(f"📋 Targeting {len(self.target_files)} root-level Python files\n")

    def validate_syntax(self, filepath):
        """Check if file has valid Python syntax"""
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", str(filepath, check=False)], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_syntax_error_line(self, filepath):
        """Get the line number of syntax error if any"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            ast.parse(content)
            return None
        except SyntaxError as e:
            return e.lineno
        except Exception:
            return None

    def fix_empty_function_bodies(self, filepath):
        """Fix empty function/class bodies by adding 'pass'"""
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            new_lines = []
            i = 0

            while i < len(lines):
                line = lines[i]
                new_lines.append(line)

                # Check if this is a function or class definition
                if re.match(r"^(\s*)(async\s+)?def\s+\w+|^(\s*)class\s+\w+", line):
                    indent = len(line) - len(line.lstrip())

                    # Check if next line exists and what it is
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        next_indent = len(next_line) - len(next_line.lstrip())

                        # If next line is not indented more (empty body) or is another def/class
                        if (
                            next_indent <= indent
                            or next_line.strip() == ""
                            or re.match(r"^\s*(def|class|async def)\s+", next_line)
                        ):
                            # Add 'pass' with proper indentation
                            new_lines.append(" " * (indent + 4) + "pass\n")
                            modified = True
                    else:
                        # Last line in file, add pass
                        new_lines.append(" " * (indent + 4) + "pass\n")
                        modified = True

                i += 1

            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                return True
            return False

        except Exception as e:
            print(f"   ⚠️  Error processing {filepath.name}: {e}")
            return False

    def fix_broken_indentation(self, filepath):
        """Fix indentation issues from docstring removal"""
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            new_lines = []
            i = 0

            while i < len(lines):
                line = lines[i]

                # Look for unexpected indent patterns
                # If line is just whitespace after a def/class, skip it
                if line.strip() == "":
                    # Check if previous line was a function/class definition
                    if i > 0 and re.match(r"^\s*(def|class|async def)\s+", new_lines[-1]):
                        # Skip empty line
                        modified = True
                        i += 1
                        continue

                new_lines.append(line)
                i += 1

            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                return True
            return False

        except Exception as e:
            print(f"   ⚠️  Error processing {filepath.name}: {e}")
            return False

    def fix_file_with_validation(self, filepath):
        """Fix a file and validate it worked"""
        filename = filepath.name

        # 1. Check if file already has syntax errors
        if not self.validate_syntax(filepath):
            print(f"🔧 Fixing {filename}...")

            # 2. Backup original content
            with open(filepath, encoding="utf-8") as f:
                original_content = f.read()

            # 3. Try fix #1: Empty function bodies
            if self.fix_empty_function_bodies(filepath):
                if self.validate_syntax(filepath):
                    print(f"   ✅ Fixed empty function bodies in {filename}")
                    self.fixes_applied += 1
                    self.files_fixed.append(filename)
                    return True

            # 4. Restore and try fix #2: Indentation
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(original_content)

            if self.fix_broken_indentation(filepath):
                if self.validate_syntax(filepath):
                    print(f"   ✅ Fixed indentation in {filename}")
                    self.fixes_applied += 1
                    self.files_fixed.append(filename)
                    return True

            # 5. Try both fixes together
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(original_content)

            self.fix_broken_indentation(filepath)
            self.fix_empty_function_bodies(filepath)

            if self.validate_syntax(filepath):
                print(f"   ✅ Fixed with combined approach in {filename}")
                self.fixes_applied += 1
                self.files_fixed.append(filename)
                return True

            # 6. If still broken, restore original and report
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(original_content)

            error_line = self.get_syntax_error_line(filepath)
            print(f"   ❌ Could not auto-fix {filename} (error at line {error_line})")
            self.files_failed.append((filename, error_line))
            return False

        return False  # File was already valid

    def run(self):
        """Run the fixer on all target files"""
        print("🔍 Phase 1: Identifying broken files...\n")

        broken_files = []
        for filepath in self.target_files:
            if not self.validate_syntax(filepath):
                broken_files.append(filepath)

        if not broken_files:
            print("✅ No broken files found! All files have valid syntax.\n")
            return

        print(f"Found {len(broken_files)} files with syntax errors\n")
        print("🔧 Phase 2: Applying safe fixes with validation...\n")

        for filepath in broken_files:
            self.fix_file_with_validation(filepath)

        print("\n" + "=" * 80)
        print("📊 Aurora's Fix Report")
        print("=" * 80)
        print(f"✅ Files successfully fixed: {len(self.files_fixed)}")
        if self.files_fixed:
            for filename in self.files_fixed:
                print(f"   • {filename}")

        if self.files_failed:
            print(f"\n❌ Files that need manual review: {len(self.files_failed)}")
            for filename, line in self.files_failed:
                print(f"   • {filename} (error at line {line})")
            print("\n💡 These files need manual inspection - my automated fix couldn't handle them")

        print(f"\n🎯 Total fixes applied: {self.fixes_applied}")

        # Final validation
        print("\n🔍 Phase 3: Final validation...\n")
        still_broken = []
        for filepath in self.target_files:
            if not self.validate_syntax(filepath):
                still_broken.append(filepath.name)

        if still_broken:
            print(f"⚠️  Still {len(still_broken)} files with syntax errors:")
            for name in still_broken[:10]:
                print(f"   • {name}")
        else:
            print("✅ All target files now have valid syntax!")

        # Run pylint to see current score
        print("\n📊 Running pylint to check current score...\n")
        try:
            result = subprocess.run(
                ["python", "-m", "pylint", "*.py", "--disable=C,R", "--max-line-length=120"],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )

            # Extract score from output
            for line in result.stdout.split("\n"):
                if "rated at" in line:
                    print(f"   {line.strip()}")
        except Exception as e:
            print(f"   Could not run pylint: {e}")


if __name__ == "__main__":
    fixer = AuroraSafeFixer()
    fixer.run()
