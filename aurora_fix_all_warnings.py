#!/usr/bin/env python3
"""
Aurora Warning Fixer - Fix all pylint warnings systematically
Focuses on: unused imports, unused variables, subprocess checks, f-strings
"""

import json
import re
import subprocess
from pathlib import Path


class AuroraWarningFixer:
    def __init__(self):
        self.fixes = 0
        self.files_modified = set()

    def get_all_errors(self):
        """Get all pylint errors including warnings"""
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

    def fix_unused_imports(self, filepath, imports_to_remove):
        """Remove unused imports"""
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                skip = False
                for imp in imports_to_remove:
                    # Match exact import patterns
                    if f"import {imp}" in line and imp in line:
                        # Check if it's the only import or part of multiple
                        if line.strip().startswith("from "):
                            # from typing import Dict, List -> remove only Dict
                            if "," in line:
                                line = line.replace(f"{imp}, ", "").replace(f", {imp}", "")
                            else:
                                skip = True
                        elif line.strip() == f"import {imp}":
                            skip = True

                if not skip:
                    new_lines.append(line)

            if len(new_lines) != len(lines):
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                self.fixes += 1
                self.files_modified.add(filepath)
                return True
        except Exception as e:
            print(f"  [WARN]  Error: {e}")
        return False

    def fix_unused_variables(self, filepath, variables):
        """Prefix unused variables with underscore"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            original = content
            for var in variables:
                if not var.startswith("_"):
                    # Pattern: var = value
                    pattern = rf"(\s){re.escape(var)}\s*="
                    content = re.sub(pattern, rf"\1_{var} =", content, count=1)

            if content != original:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                self.fixes += 1
                self.files_modified.add(filepath)
                return True
        except Exception as e:
            print(f"  [WARN]  Error: {e}")
        return False

    def fix_subprocess_check(self, filepath):
        """Add check=False to subprocess.run calls"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            original = content
            # Find subprocess.run without check parameter
            pattern = r"subprocess\.run\s*\([^)]*\)"

            def add_check(match):
                call = match.group(0)
                if "check=" not in call:
                    # Add check=False before closing paren
                    if call.endswith(")"):
                        return call[:-1] + ", check=False)"
                return call

            content = re.sub(pattern, add_check, content, flags=re.DOTALL)

            if content != original:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                self.fixes += 1
                self.files_modified.add(filepath)
                return True
        except Exception as e:
            print(f"  [WARN]  Error: {e}")
        return False

    def fix_f_strings(self, filepath, line_numbers):
        """Remove f prefix from strings without interpolation"""
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            for line_num in line_numbers:
                idx = line_num - 1
                if idx < len(lines):
                    line = lines[idx]
                    if ('f"' in line or "f'" in line) and "{" not in line:
                        lines[idx] = line.replace('f"', '"').replace("f'", "'")
                        modified = True

            if modified:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                self.fixes += 1
                self.files_modified.add(filepath)
                return True
        except Exception as e:
            print(f"  [WARN]  Error: {e}")
        return False

    def fix_bare_except(self, filepath):
        """Change bare except: to except Exception:"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            original = content
            content = re.sub(r"\bexcept\s*:\s*\n", "except Exception:\n", content)

            if content != original:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                self.fixes += 1
                self.files_modified.add(filepath)
                return True
        except Exception as e:
            print(f"  [WARN]  Error: {e}")
        return False

    def fix_all(self):
        """Main fix function"""
        print("[SCAN] Aurora scanning all warnings...\n")

        errors = self.get_all_errors()
        print(f"[DATA] Found {len(errors)} issues\n")

        # Group by file and type
        by_file = {}
        for error in errors:
            filepath = error["path"]
            msg_id = error.get("message-id", error.get("symbol", ""))

            if filepath not in by_file:
                by_file[filepath] = {
                    "unused-import": [],
                    "unused-variable": [],
                    "subprocess-run-check": [],
                    "f-string-without-interpolation": [],
                    "bare-except": [],
                    "other": [],
                }

            if "unused-import" in msg_id or "unused-import" in error.get("symbol", ""):
                # Extract import name from message
                match = re.search(r"'([^']+)'", error["message"])
                if match:
                    by_file[filepath]["unused-import"].append(match.group(1))
            elif "unused-variable" in msg_id or "unused-variable" in error.get("symbol", ""):
                match = re.search(r"'([^']+)'", error["message"])
                if match:
                    by_file[filepath]["unused-variable"].append(match.group(1))
            elif "subprocess-run-check" in msg_id or "subprocess-run-check" in error.get("symbol", ""):
                by_file[filepath]["subprocess-run-check"].append(error["line"])
            elif "f-string-without-interpolation" in msg_id or "f-string-without-interpolation" in error.get(
                "symbol", ""
            ):
                by_file[filepath]["f-string-without-interpolation"].append(error["line"])
            elif "bare-except" in msg_id or "bare-except" in error.get("symbol", ""):
                by_file[filepath]["bare-except"].append(error["line"])

        # Fix each file
        for filepath, issues in sorted(by_file.items()):
            print(f"[EMOJI] {Path(filepath).name}:")

            if issues["unused-import"]:
                print(f"  Removing {len(issues['unused-import'])} unused imports...")
                self.fix_unused_imports(filepath, issues["unused-import"])

            if issues["unused-variable"]:
                print(f"  Fixing {len(issues['unused-variable'])} unused variables...")
                self.fix_unused_variables(filepath, issues["unused-variable"])

            if issues["subprocess-run-check"]:
                print("  Adding check=False to subprocess calls...")
                self.fix_subprocess_check(filepath)

            if issues["f-string-without-interpolation"]:
                print(f"  Fixing {len(issues['f-string-without-interpolation'])} f-strings...")
                self.fix_f_strings(filepath, issues["f-string-without-interpolation"])

            if issues["bare-except"]:
                print("  Fixing bare except clauses...")
                self.fix_bare_except(filepath)

        # Verify
        print("\n\n[TEST] Running final check...\n")
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

        print(f"\n[SPARKLE] Aurora applied {self.fixes} fixes to {len(self.files_modified)} files")


if __name__ == "__main__":
    fixer = AuroraWarningFixer()
    fixer.fix_all()
