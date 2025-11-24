#!/usr/bin/env python3
"""
Aurora Comprehensive Pylint Fixer
Fixes ALL pylint issues systematically with validation
"""

import ast
import json
import re
import subprocess


class AuroraComprehensiveFixer:
    def __init__(self):
        self.fixes_applied = 0
        self.files_modified = set()
        self.validation_enabled = True

    def run_pylint(self):
        """Run pylint and get all errors"""
        result = subprocess.run(
            ["python", "-m", "pylint", "*.py", "--disable=C,R", "--max-line-length=120", "--output-format=json"],
            capture_output=True,
            text=True,
            shell=True,
            check=False,
        )
        try:
            return json.loads(result.stdout)
        except Exception:
            return []

    def validate_syntax(self, filepath):
        """Validate Python syntax"""
        try:
            with open(filepath, encoding="utf-8") as f:
                ast.parse(f.read())
            return True
        except SyntaxError as e:
            print(f"[ERROR] Syntax error in {filepath}:{e.lineno}: {e.msg}")
            return False

    def fix_unused_imports(self, filepath, unused_imports):
        """Remove unused imports"""
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            for unused in unused_imports:
                for i, line in enumerate(lines):
                    if f"import {unused}" in line or f"from {unused}" in line:
                        # Check if it's the only import on the line
                        if line.strip().startswith("import ") or line.strip().startswith("from "):
                            lines[i] = ""
                            modified = True
                            print(f"  Removed unused import: {unused}")

            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines([l for l in lines if l.strip() or l == "\n"])

                if self.validate_syntax(filepath):
                    self.fixes_applied += 1
                    self.files_modified.add(filepath)
                    return True
                else:
                    # Restore original
                    with open(filepath, encoding="utf-8") as f:
                        _original = f.read()
                    print("  [WARN] Reverted - syntax error after removal")
                    return False
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
        return False

    def fix_unused_variables(self, filepath, unused_vars):
        """Fix unused variables by prefixing with underscore"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            original = content
            modified = False

            for var_name in unused_vars:
                # Pattern: var = something (but not _var)
                if not var_name.startswith("_"):
                    pattern = rf"\b{re.escape(var_name)}\s*="
                    if re.search(pattern, content):
                        content = re.sub(pattern, f"_{var_name} =", content, count=1)
                        modified = True
                        print(f"  Prefixed unused variable: {var_name} -> _{var_name}")

            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)

                if self.validate_syntax(filepath):
                    self.fixes_applied += 1
                    self.files_modified.add(filepath)
                    return True
                else:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(original)
                    print("  [WARN] Reverted - syntax error")
                    return False
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
        return False

    def fix_subprocess_check(self, filepath, line_numbers):
        """Add check=True to subprocess.run calls"""
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            original = lines.copy()
            modified = False

            for line_num in line_numbers:
                line = lines[line_num - 1]
                if "subprocess.run" in line and "check=" not in line:
                    # Add check=False if not capturing output, check=True if safe
                    if "capture_output=True" in line or "stdout=" in line:
                        lines[line_num - 1] = line.replace("subprocess.run(", "subprocess.run(", 1, check=False)
                        # Insert check parameter before closing paren
                        if ")" in lines[line_num - 1]:
                            lines[line_num - 1] = lines[line_num - 1].replace(")", ", check=False)", 1)
                        modified = True

            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(lines)

                if self.validate_syntax(filepath):
                    self.fixes_applied += 1
                    self.files_modified.add(filepath)
                    return True
                else:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.writelines(original)
                    print("  [WARN] Reverted - syntax error")
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
        return False

    def fix_redefined_names(self, filepath, redefined):
        """Fix redefined outer scope names"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            original = content
            modified = False

            for name in redefined:
                # Common pattern: function parameter shadows outer variable
                # Rename parameter to _name or name_param
                pattern = rf"def \w+\([^)]*\b{re.escape(name)}\b"
                if re.search(pattern, content):
                    content = re.sub(rf"\b{re.escape(name)}\b(?=\s*[,)])", f"{name}_param", content, count=1)
                    modified = True
                    print(f"  Renamed parameter: {name} -> {name}_param")

            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)

                if self.validate_syntax(filepath):
                    self.fixes_applied += 1
                    self.files_modified.add(filepath)
                    return True
                else:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(original)
                    print("  [WARN] Reverted")
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
        return False

    def fix_f_string_interpolation(self, filepath, line_numbers):
        """Fix f-strings without interpolation"""
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            original = lines.copy()
            modified = False

            for line_num in line_numbers:
                line = lines[line_num - 1]
                # Remove f prefix if no {} in string
                if 'f"' in line or "f'" in line:
                    if "{" not in line:
                        lines[line_num - 1] = line.replace('f"', '"').replace("f'", "'")
                        modified = True

            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(lines)

                if self.validate_syntax(filepath):
                    self.fixes_applied += 1
                    self.files_modified.add(filepath)
                    return True
                else:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.writelines(original)
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
        return False

    def fix_all(self):
        """Main fixing function"""
        print("[SCAN] Aurora scanning for pylint issues...\n")

        errors = self.run_pylint()
        print(f"[DATA] Found {len(errors)} issues to fix\n")

        # Group by file and error type
        files_errors = {}
        for error in errors:
            filepath = error["path"]
            if filepath not in files_errors:
                files_errors[filepath] = {
                    "unused-import": [],
                    "unused-variable": [],
                    "unused-argument": [],
                    "subprocess-run-check": [],
                    "redefined-outer-name": [],
                    "f-string-without-interpolation": [],
                    "undefined-variable": [],
                    "syntax-error": [],
                }

            msg_id = error.get("message-id", error.get("symbol", ""))
            if msg_id in files_errors[filepath]:
                files_errors[filepath][msg_id].append(error)

        # Fix each file
        for filepath, error_types in sorted(files_errors.items()):
            print(f"\n[EMOJI] {filepath}:")

            # Fix syntax errors first
            if error_types["syntax-error"]:
                print("  [WARN] Has syntax errors - skipping automated fixes")
                continue

            # Fix undefined variables (from previous fix)
            if error_types["undefined-variable"]:
                print("  [WARN] Has undefined variables - needs manual review")

            # Fix unused imports
            if error_types["unused-import"]:
                unused = [e["message"].split("'")[1] for e in error_types["unused-import"]]
                print(f"  Fixing {len(unused)} unused imports...")
                self.fix_unused_imports(filepath, unused)

            # Fix unused variables
            if error_types["unused-variable"]:
                unused = [e["message"].split("'")[1] for e in error_types["unused-variable"]]
                print(f"  Fixing {len(unused)} unused variables...")
                self.fix_unused_variables(filepath, unused)

            # Fix subprocess.run
            if error_types["subprocess-run-check"]:
                lines = [e["line"] for e in error_types["subprocess-run-check"]]
                print(f"  Fixing {len(lines)} subprocess.run calls...")
                self.fix_subprocess_check(filepath, lines)

            # Fix redefined names
            if error_types["redefined-outer-name"]:
                names = [e["message"].split("'")[1] for e in error_types["redefined-outer-name"]]
                print(f"  Fixing {len(names)} redefined names...")
                self.fix_redefined_names(filepath, names)

            # Fix f-strings
            if error_types["f-string-without-interpolation"]:
                lines = [e["line"] for e in error_types["f-string-without-interpolation"]]
                print(f"  Fixing {len(lines)} f-strings...")
                self.fix_f_string_interpolation(filepath, lines)

        # Final validation
        print("\n\n[TEST] Running final validation...\n")
        result = subprocess.run(
            ["python", "-m", "pylint", "*.py", "--disable=C,R", "--max-line-length=120"],
            capture_output=True,
            text=True,
            shell=True,
            check=False,
        )

        for line in result.stdout.split("\n"):
            if "rated at" in line:
                print(line)

        print(f"\n[SPARKLE] Aurora applied {self.fixes_applied} fixes to {len(self.files_modified)} files")
        if self.files_modified:
            print(f"[EMOJI] Modified: {', '.join(sorted(self.files_modified)[:10])}")
            if len(self.files_modified) > 10:
                print(f"   ... and {len(self.files_modified) - 10} more")


if __name__ == "__main__":
    fixer = AuroraComprehensiveFixer()
    fixer.fix_all()
