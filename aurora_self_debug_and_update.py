#!/usr/bin/env python3
"""
import time
Aurora Self-Debug, Self-Fix, and Self-Update System
Aurora autonomously scans, debugs, fixes, and updates her entire system
Frontend + Backend + Python + Everything
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class AuroraSelfDebugSystem:
    """Aurora's autonomous self-debugging and self-updating system"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors_found = []
        self.fixes_applied = []
        self.updates_made = []
        self.scan_results = {"python": [], "typescript": [], "javascript": [], "json": [], "yaml": [], "dockerfile": []}

    def log(self, message: str, level: str = "INFO"):
        """Log Aurora's actions"""
        _timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "[STAR]", "SUCCESS": "[OK]", "ERROR": "[ERROR]", "FIX": "[EMOJI]", "UPDATE": "[SYNC]"}.get(level, "ℹ️")
        print(f"[{timestamp}] {prefix} Aurora: {message}")

    def run_command(self, command: str, cwd: Path = None) -> dict[str, Any]:
        """Run a command and capture output"""
        try:
            result = subprocess.run(
                command, shell=True, cwd=cwd or self.project_root, capture_output=True, text=True, timeout=300
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": "Command timed out", "returncode": -1}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}

    def scan_python_errors(self):
        """Scan for Python syntax errors and type issues"""
        self.log("Scanning Python files for errors...", "INFO")

        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if ".venv" not in str(f) and "node_modules" not in str(f)]

        self.log(f"Found {len(python_files)} Python files to check")

        errors = []
        for py_file in python_files:
            # Check syntax
            result = self.run_command(f'python -m py_compile "{py_file}"')
            if not result["success"]:
                errors.append(
                    {
                        "file": str(py_file.relative_to(self.project_root)),
                        "type": "syntax_error",
                        "error": result["stderr"],
                    }
                )

        self.scan_results["python"] = errors
        if errors:
            self.log(f"Found {len(errors)} Python errors", "ERROR")
        else:
            self.log("No Python syntax errors found", "SUCCESS")

        return errors

    def scan_typescript_errors(self):
        """Scan TypeScript/JavaScript for errors"""
        self.log("Scanning TypeScript/JavaScript files...", "INFO")

        # Check if we have TypeScript
        if not (self.project_root / "tsconfig.json").exists():
            self.log("No tsconfig.json found, skipping TypeScript check")
            return []

        # Run TypeScript compiler check
        result = self.run_command("npx tsc --noEmit")

        errors = []
        if not result["success"]:
            # Parse TypeScript errors
            for line in result["stdout"].split("\n"):
                if "error TS" in line:
                    errors.append({"type": "typescript_error", "error": line.strip()})

        self.scan_results["typescript"] = errors
        if errors:
            self.log(f"Found {len(errors)} TypeScript errors", "ERROR")
        else:
            self.log("No TypeScript errors found", "SUCCESS")

        return errors

    def scan_eslint_issues(self):
        """Scan for ESLint issues in frontend"""
        self.log("Running ESLint on frontend...", "INFO")

        if not (self.project_root / "client").exists():
            self.log("No client directory found")
            return []

        result = self.run_command("npm run lint --prefix client")

        issues = []
        if not result["success"]:
            issues.append({"type": "eslint_issues", "output": result["stdout"]})
            self.log("ESLint found issues", "ERROR")
        else:
            self.log("No ESLint issues found", "SUCCESS")

        return issues

    def fix_common_python_issues(self):
        """Fix common Python issues automatically"""
        self.log("Attempting to fix Python issues...", "FIX")

        fixes = 0

        # Run autopep8 for formatting
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if ".venv" not in str(f)]

        for py_file in python_files:
            # Skip if file is in excluded paths
            if any(excluded in str(py_file) for excluded in [".venv", "node_modules", "__pycache__"]):
                continue

            result = self.run_command(f'python -m autopep8 --in-place --aggressive "{py_file}"')
            if result["success"]:
                fixes += 1

        if fixes > 0:
            self.log(f"Applied autopep8 fixes to {fixes} files", "SUCCESS")
            self.fixes_applied.append(f"autopep8: {fixes} files")

        return fixes

    def fix_typescript_issues(self):
        """Fix TypeScript issues automatically"""
        self.log("Attempting to fix TypeScript issues...", "FIX")

        # Run ESLint fix
        result = self.run_command("npm run lint:fix --prefix client")

        if result["success"]:
            self.log("Applied ESLint fixes", "SUCCESS")
            self.fixes_applied.append("eslint --fix")
            return True
        else:
            self.log("Could not apply all ESLint fixes", "ERROR")
            return False

    def update_dependencies(self):
        """Check and update dependencies"""
        self.log("Checking for dependency updates...", "UPDATE")

        updates = []

        # Check Python dependencies
        if (self.project_root / "requirements.txt").exists():
            self.log("Checking Python dependencies...")
            result = self.run_command("pip list --outdated --format=json")
            if result["success"]:
                try:
                    outdated = json.loads(result["stdout"])
                    if outdated:
                        self.log(f"Found {len(outdated)} outdated Python packages")
                        updates.append(f"Python: {len(outdated)} packages")
                except:
                    pass

        # Check npm dependencies
        if (self.project_root / "package.json").exists():
            self.log("Checking npm dependencies...")
            result = self.run_command("npm outdated --json")
            if result["stdout"]:
                try:
                    outdated = json.loads(result["stdout"])
                    if outdated:
                        self.log(f"Found {len(outdated)} outdated npm packages")
                        updates.append(f"npm: {len(outdated)} packages")
                except:
                    pass

        # Check client npm dependencies
        if (self.project_root / "client" / "package.json").exists():
            self.log("Checking client npm dependencies...")
            result = self.run_command("npm outdated --json", cwd=self.project_root / "client")
            if result["stdout"]:
                try:
                    outdated = json.loads(result["stdout"])
                    if outdated:
                        self.log(f"Found {len(outdated)} outdated client packages")
                        updates.append(f"client npm: {len(outdated)} packages")
                except:
                    pass

        self.updates_made.extend(updates)
        return updates

    def scan_for_red_squiggles(self):
        """Scan for common code issues that would show as red squiggles in IDE"""
        self.log("Scanning for IDE-level issues (red squiggles)...", "INFO")

        issues = []

        # Check for undefined variables, unused imports, etc.
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if ".venv" not in str(f)]

        for py_file in python_files:
            try:
                content = py_file.read_text(encoding="utf-8")

                # Check for common issues
                if "import *" in content:
                    issues.append(
                        {
                            "file": str(py_file.relative_to(self.project_root)),
                            "issue": "Wildcard import detected",
                            "severity": "warning",
                        }
                    )

                # Check for unused variables (basic check)
                if re.search(r"^\s*def\s+\w+\([^)]*\)\s*:\s*pass\s*$", content, re.MULTILINE):
                    issues.append(
                        {
                            "file": str(py_file.relative_to(self.project_root)),
                            "issue": "Empty function with pass",
                            "severity": "info",
                        }
                    )

            except Exception as e:
                self.log(f"Could not scan {py_file}: {e}", "ERROR")

        if issues:
            self.log(f"Found {len(issues)} potential IDE issues", "ERROR")
        else:
            self.log("No IDE-level issues detected", "SUCCESS")

        return issues

    def run_comprehensive_debug(self):
        """Run complete system-wide debug"""
        self.log("[LAUNCH] Starting Aurora's Comprehensive Self-Debug System", "INFO")
        self.log("=" * 80)

        # Phase 1: Scan
        self.log("\n[DATA] PHASE 1: SCANNING", "INFO")
        self.log("-" * 80)

        python_errors = self.scan_python_errors()
        ts_errors = self.scan_typescript_errors()
        eslint_issues = self.scan_eslint_issues()
        ide_issues = self.scan_for_red_squiggles()

        # Phase 2: Fix
        self.log("\n[EMOJI] PHASE 2: FIXING", "INFO")
        self.log("-" * 80)

        self.fix_common_python_issues()
        self.fix_typescript_issues()

        # Phase 3: Update
        self.log("\n[SYNC] PHASE 3: UPDATING", "INFO")
        self.log("-" * 80)

        updates = self.update_dependencies()

        # Phase 4: Final Report
        self.log("\n[EMOJI] FINAL REPORT", "INFO")
        self.log("=" * 80)

        total_errors = len(python_errors) + len(ts_errors) + len(eslint_issues) + len(ide_issues)

        print(f"\n[SCAN] Errors Found: {total_errors}")
        print(f"   • Python errors: {len(python_errors)}")
        print(f"   • TypeScript errors: {len(ts_errors)}")
        print(f"   • ESLint issues: {len(eslint_issues)}")
        print(f"   • IDE issues: {len(ide_issues)}")

        print(f"\n[OK] Fixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"   • {fix}")

        print(f"\n[SYNC] Updates Available: {len(updates)}")
        for update in updates:
            print(f"   • {update}")

        # Save detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "errors_found": {
                "python": python_errors,
                "typescript": ts_errors,
                "eslint": eslint_issues,
                "ide": ide_issues,
            },
            "fixes_applied": self.fixes_applied,
            "updates_available": updates,
            "summary": {
                "total_errors": total_errors,
                "total_fixes": len(self.fixes_applied),
                "total_updates": len(updates),
            },
        }

        report_file = self.project_root / "AURORA_SELF_DEBUG_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.log(f"\n[EMOJI] Detailed report saved to: {report_file.name}", "SUCCESS")

        if total_errors == 0:
            self.log("\n[EMOJI] Aurora is running clean! No errors detected.", "SUCCESS")
        else:
            self.log(f"\n[WARN]  {total_errors} issues need attention", "ERROR")

        self.log("=" * 80)
        self.log("[STAR] Aurora Self-Debug Complete!", "SUCCESS")

        return report


def main():
    """Main entry point"""
    print(
        """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                   [STAR] AURORA SELF-DEBUG & UPDATE SYSTEM [STAR]                   ║
║                                                                              ║
║                    Aurora Autonomously Debugging Herself                     ║
║                   Frontend • Backend • Python • Everything                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    )

    aurora_debug = AuroraSelfDebugSystem()
    report = aurora_debug.run_comprehensive_debug()

    return 0 if report["summary"]["total_errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
