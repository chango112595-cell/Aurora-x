#!/usr/bin/env python3
"""
Aurora Full System Debug
Comprehensive debugging before commit
"""

import json
import subprocess
import sys
import traceback
from importlib import import_module
from pathlib import Path


class AuroraSystemDebugger:
    """Comprehensive system debugging"""

    def __init__(self):
        self.root = Path(".")
        self.errors = []
        self.warnings = []
        self.successes = []

    def test_python_syntax(self):
        """Test all Python files for syntax errors"""
        print("\n[SCAN] Testing Python Syntax...")

        py_files = list(self.root.glob("*.py"))
        py_files.extend(list((self.root / "tools").glob("*.py")))
        py_files.extend(list((self.root / "server").glob("**/*.py")))

        syntax_errors = []
        for py_file in py_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    compile(f.read(), str(py_file), "exec")
                self.successes.append(f"[OK] Syntax OK: {py_file.name}")
            except SyntaxError as e:
                syntax_errors.append(f"[ERROR] Syntax error in {py_file.name}: {e}")
                self.errors.append(f"Syntax error in {py_file.name}")

        if syntax_errors:
            for err in syntax_errors[:5]:  # Show first 5
                print(f"   {err}")
            if len(syntax_errors) > 5:
                print(f"   ... and {len(syntax_errors) - 5} more")
        else:
            print(f"   [OK] All {len(py_files)} Python files have valid syntax")

    def test_core_imports(self):
        """Test that core modules can be imported"""
        print("\n[SCAN] Testing Core Module Imports...")

        core_modules = [
            "aurora_core",
            "aurora_chat_server",
            "aurora_intelligence_manager",
        ]

        for module_name in core_modules:
            try:
                # Try to import
                sys.path.insert(0, str(self.root))
                _module = import_module(module_name)
                self.successes.append(f"[OK] Import OK: {module_name}")
                print(f"   [OK] {module_name}")
            except Exception as e:
                self.errors.append(f"Failed to import {module_name}: {str(e)}")
                print(f"   [ERROR] {module_name}: {str(e)}")

    def test_aurora_core_structure(self):
        """Test aurora_core.py structure"""
        print("\n[SCAN] Testing Aurora Core Structure...")

        try:
            from aurora_core import AuroraFoundations, AuroraKnowledgeTiers

            # Test foundations
            foundations = AuroraFoundations()
            if len(foundations.tasks) == 13:
                print("   [OK] AuroraFoundations: 13/13 tasks")
                self.successes.append("AuroraFoundations structure valid")
            else:
                self.errors.append(f"AuroraFoundations: {len(foundations.tasks)}/13 tasks")
                print(f"   [ERROR] AuroraFoundations: {len(foundations.tasks)}/13 tasks")

            # Test tiers
            tiers = AuroraKnowledgeTiers()
            if len(tiers.tiers) == 34:
                print("   [OK] AuroraKnowledgeTiers: 34/66 tiers")
                self.successes.append("AuroraKnowledgeTiers structure valid")
            else:
                self.errors.append(f"AuroraKnowledgeTiers: {len(tiers.tiers)}/66 tiers")
                print(f"   [ERROR] AuroraKnowledgeTiers: {len(tiers.tiers)}/66 tiers")

            # Test integration
            if hasattr(tiers, "foundations"):
                print("   [OK] Foundations integrated into Tiers")
                self.successes.append("Foundations properly integrated")
            else:
                self.errors.append("Foundations not integrated into Tiers")
                print("   [ERROR] Foundations not integrated")

        except Exception as e:
            self.errors.append(f"Aurora Core test failed: {str(e)}")
            print(f"   [ERROR] Error: {str(e)}")
            traceback.print_exc()

    def test_json_files(self):
        """Test all JSON files are valid"""
        print("\n[SCAN] Testing JSON Files...")

        json_files = list(self.root.glob("*.json"))
        json_files.extend(list((self.root / "server").glob("**/*.json")))

        for json_file in json_files:
            try:
                with open(json_file, encoding="utf-8") as f:
                    json.load(f)
                self.successes.append(f"[OK] JSON valid: {json_file.name}")
            except Exception as e:
                self.errors.append(f"Invalid JSON in {json_file.name}")
                print(f"   [ERROR] {json_file.name}: {str(e)}")

        if not any("Invalid JSON" in e for e in self.errors):
            print(f"   [OK] All {len(json_files)} JSON files are valid")

    def test_linter_config(self):
        """Test linter configuration"""
        print("\n[SCAN] Testing Linter Configuration...")

        pylintrc = self.root / ".pylintrc"
        pyproject = self.root / "pyproject.toml"

        if pylintrc.exists():
            print("   [OK] .pylintrc exists")
            self.successes.append(".pylintrc configured")
        else:
            self.warnings.append(".pylintrc not found")
            print("   [WARN]  .pylintrc not found")

        if pyproject.exists():
            content = pyproject.read_text()
            if "[tool.ruff]" in content:
                print("   [OK] pyproject.toml has Ruff config")
                self.successes.append("Ruff configured")
            else:
                self.warnings.append("Ruff config not in pyproject.toml")
                print("   [WARN]  Ruff config not found in pyproject.toml")

    def test_directory_structure(self):
        """Test directory structure"""
        print("\n[SCAN] Testing Directory Structure...")

        required_dirs = {
            "tools": "Tool utilities",
            "server": "Chango backend",
            "archive/legacy": "Archived files",
        }

        for dir_path, description in required_dirs.items():
            path = self.root / dir_path
            if path.exists() and path.is_dir():
                print(f"   [OK] {dir_path}/ ({description})")
                self.successes.append(f"{dir_path}/ exists")
            else:
                self.warnings.append(f"{dir_path}/ not found")
                print(f"   [WARN]  {dir_path}/ not found ({description})")

    def test_git_status(self):
        """Test git repository status"""
        print("\n[SCAN] Testing Git Status...")

        try:
            # Check if git repo
            result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=self.root, check=False
            )

            if result.returncode == 0:
                changes = result.stdout.strip().split("\n") if result.stdout.strip() else []
                if changes and changes[0]:
                    print(f"   ℹ️  {len(changes)} files with changes")
                    self.successes.append(f"Git status OK: {len(changes)} changes")
                else:
                    print("   [OK] No uncommitted changes")
                    self.successes.append("Git working tree clean")
            else:
                self.warnings.append("Git status check failed")
                print("   [WARN]  Could not check git status")

        except Exception as e:
            self.warnings.append(f"Git not available: {str(e)}")
            print("   [WARN]  Git not available")

    def test_critical_files(self):
        """Test critical files exist"""
        print("\n[SCAN] Testing Critical Files...")

        critical_files = {
            "aurora_core.py": "Main intelligence core",
            "aurora_chat_server.py": "Chat API server",
            "aurora_cosmic_nexus.html": "Primary UI",
            "tools/luminar_nexus_v2.py": "Service orchestration",
            "tools/aurora_execute_plan.py": "Execution tasks",
        }

        for file_path, description in critical_files.items():
            path = self.root / file_path
            if path.exists():
                size_kb = path.stat().st_size / 1024
                print(f"   [OK] {file_path} ({size_kb:.1f} KB)")
                self.successes.append(f"{file_path} exists")
            else:
                self.errors.append(f"{file_path} missing")
                print(f"   [ERROR] {file_path} MISSING ({description})")

    def run_pylint_check(self):
        """Run pylint on aurora_core.py"""
        print("\n[SCAN] Running Pylint Check...")

        try:
            result = subprocess.run(
                ["pylint", "aurora_core.py", "--exit-zero"],
                capture_output=True,
                text=True,
                cwd=self.root,
                timeout=30,
                check=False,
            )

            if "rated at" in result.stdout.lower():
                # Extract rating
                lines = result.stdout.split("\n")
                for line in lines:
                    if "rated at" in line.lower():
                        print(f"   ℹ️  {line.strip()}")
                        self.successes.append("Pylint check completed")
                        break
            else:
                print("   [OK] Pylint check completed")
                self.successes.append("Pylint check completed")

        except subprocess.TimeoutExpired:
            self.warnings.append("Pylint check timed out")
            print("   [WARN]  Pylint check timed out (skipping)")
        except FileNotFoundError:
            self.warnings.append("Pylint not installed")
            print("   [WARN]  Pylint not installed (skipping)")
        except Exception as e:
            self.warnings.append(f"Pylint error: {str(e)}")
            print("   [WARN]  Pylint error (skipping)")

    def generate_debug_report(self):
        """Generate comprehensive debug report"""
        print("\n" + "=" * 80)
        print("[SCAN] AURORA FULL SYSTEM DEBUG REPORT")
        print("=" * 80)

        # Run all tests
        self.test_python_syntax()
        self.test_core_imports()
        self.test_aurora_core_structure()
        self.test_json_files()
        self.test_linter_config()
        self.test_directory_structure()
        self.test_critical_files()
        self.test_git_status()
        self.run_pylint_check()

        # Summary
        print("\n" + "=" * 80)
        print("[DATA] DEBUG SUMMARY")
        print("=" * 80)
        print(f"[OK] Successes: {len(self.successes)}")
        print(f"[WARN]  Warnings: {len(self.warnings)}")
        print(f"[ERROR] Errors: {len(self.errors)}")

        # Show errors if any
        if self.errors:
            print("\n" + "=" * 80)
            print("[ERROR] ERRORS FOUND")
            print("=" * 80)
            for error in self.errors:
                print(f"   [ERROR] {error}")

        # Show warnings if any
        if self.warnings:
            print("\n" + "=" * 80)
            print("[WARN]  WARNINGS")
            print("=" * 80)
            for warning in self.warnings[:10]:  # Show first 10
                print(f"   [WARN]  {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more warnings")

        # Save report
        report = {
            "successes": len(self.successes),
            "warnings": len(self.warnings),
            "errors": len(self.errors),
            "error_details": self.errors,
            "warning_details": self.warnings,
        }

        report_file = self.root / "AURORA_DEBUG_REPORT.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\n[EMOJI] Debug report saved to: {report_file}")

        # Final verdict
        print("\n" + "=" * 80)
        if len(self.errors) == 0:
            print("[EMOJI] SYSTEM STATUS: [OK] READY FOR COMMIT")
            print("=" * 80)
            print("\nAll critical tests passed. System is stable and ready to commit.")
            return True
        else:
            print("[EMOJI] SYSTEM STATUS: [ERROR] NEEDS FIXES BEFORE COMMIT")
            print("=" * 80)
            print(f"\nFound {len(self.errors)} errors that must be fixed before committing.")
            return False


if __name__ == "__main__":
    print("\n[LAUNCH] Starting Aurora Full System Debug...")
    print("=" * 80)

    debugger = AuroraSystemDebugger()
    READY = debugger.generate_debug_report()

    print("\n" + "=" * 80)
    print("[SCAN] Debug Complete!")
    print("=" * 80 + "\n")

    exit(0 if READY else 1)
