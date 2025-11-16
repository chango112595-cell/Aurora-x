#!/usr/bin/env python3
"""
Aurora Comprehensive System Verification
Analyzes the entire project to ensure everything is where it belongs
"""

import json
import re
from pathlib import Path


class AuroraSystemVerification:
    """Aurora's self-verification system"""

    def __init__(self):
        self.root = Path(".")
        self.issues = []
        self.successes = []
        self.recommendations = []

    def verify_core_structure(self):
        """Verify aurora_core.py has proper structure"""
        print("\n🔍 Verifying Aurora Core Structure...")

        core_file = self.root / "aurora_core.py"
        if not core_file.exists():
            self.issues.append("❌ aurora_core.py NOT FOUND")
            return

        content = core_file.read_text(encoding="utf-8")

        # Check for Task1-13 Foundations
        if "class AuroraFoundations:" in content:
            self.successes.append("✅ AuroraFoundations class found")

            # Verify all 13 tasks
            tasks_found = []
            for i in range(1, 14):
                task_name = f"task_{i:02d}"
                if task_name in content:
                    tasks_found.append(task_name)

            if len(tasks_found) == 13:
                self.successes.append(
                    f"✅ All 13 foundational tasks present: {', '.join(tasks_found)}")
            else:
                self.issues.append(
                    f"❌ Only {len(tasks_found)}/13 tasks found: {tasks_found}")
        else:
            self.issues.append(
                "❌ AuroraFoundations class NOT FOUND in aurora_core.py")

        # Check for Tier1-34 Knowledge
        if "class AuroraKnowledgeTiers:" in content:
            self.successes.append("✅ AuroraKnowledgeTiers class found")

            # Verify all 34 tiers
            tiers_found = []
            for i in range(1, 35):
                tier_name = f"tier_{i:02d}"
                if tier_name in content:
                    tiers_found.append(tier_name)

            if len(tiers_found) == 34:
                self.successes.append("✅ All 34 knowledge tiers present")
            else:
                self.issues.append(f"❌ Only {len(tiers_found)}/34 tiers found")
        else:
            self.issues.append("❌ AuroraKnowledgeTiers class NOT FOUND")

        # Check integration
        if "self.foundations = AuroraFoundations()" in content:
            self.successes.append(
                "✅ Foundations properly integrated into AuroraKnowledgeTiers")
        else:
            self.issues.append(
                "❌ Foundations NOT integrated into AuroraKnowledgeTiers.__init__")

    def verify_service_files(self):
        """Verify service orchestration files"""
        print("\n🔍 Verifying Service Files...")

        services = {
            "tools/luminar_nexus_v2.py": "Service orchestration",
            "aurora_chat_server.py": "Chat API server",
            "aurora_intelligence_manager.py": "Intelligence coordination",
        }

        for service_file, description in services.items():
            path = self.root / service_file
            if path.exists():
                self.successes.append(
                    f"✅ {service_file} found ({description})")
            else:
                self.issues.append(
                    f"❌ {service_file} NOT FOUND - {description}")

    def verify_tools_organization(self):
        """Verify tools directory is properly organized"""
        print("\n🔍 Verifying Tools Organization...")

        tools_dir = self.root / "tools"
        if not tools_dir.exists():
            self.issues.append("❌ tools/ directory NOT FOUND")
            return

        self.successes.append("✅ tools/ directory exists")

        # Count tool files
        tool_files = list(tools_dir.glob("aurora_*.py"))
        self.successes.append(
            f"✅ Found {len(tool_files)} tool files in tools/")

        # Check for execution plan (Task1-7 execution tasks)
        exec_plan = tools_dir / "aurora_execute_plan.py"
        if exec_plan.exists():
            self.successes.append(
                "✅ aurora_execute_plan.py in tools/ (execution tasks)")
        else:
            self.issues.append("❌ aurora_execute_plan.py NOT in tools/")

    def verify_frontend_structure(self):
        """Verify frontend structure"""
        print("\n🔍 Verifying Frontend Structure...")

        frontend_files = {
            "aurora_cosmic_nexus.html": "Cosmic Nexus UI",
            "aurora_minimal_chat.html": "Minimal chat interface",
        }

        for file, description in frontend_files.items():
            path = self.root / file
            if path.exists():
                self.successes.append(f"✅ {file} found ({description})")

    def verify_backend_structure(self):
        """Verify Chango backend structure"""
        print("\n🔍 Verifying Chango Backend...")

        server_dir = self.root / "server"
        if not server_dir.exists():
            self.issues.append(
                "❌ server/ directory NOT FOUND (Chango backend)")
            return

        self.successes.append("✅ server/ directory exists (Chango backend)")

        # Check key backend files
        key_files = {
            "server/package.json": "Node.js dependencies",
            "server/tsconfig.json": "TypeScript config",
        }

        for file, description in key_files.items():
            path = self.root / file
            if path.exists():
                self.successes.append(f"✅ {file} found ({description})")

    def check_duplicate_tiers(self):
        """Check for files that duplicate tier definitions"""
        print("\n🔍 Checking for Duplicate Tier Definitions...")

        # Files that should import from aurora_core, not redefine tiers
        files_to_check = [
            "aurora_foundational_genius.py",
            "aurora_grandmaster_skills_registry.py",
            "aurora_grandmaster_training.py",
        ]

        for file_name in files_to_check:
            path = self.root / file_name
            if path.exists():
                content = path.read_text(encoding="utf-8")

                # Check if it properly imports from aurora_core
                if "from aurora_core import" in content or "import aurora_core" in content:
                    self.successes.append(
                        f"✅ {file_name} properly imports from aurora_core")
                # Check if it defines tier methods (not allowed)
                elif "def _get_tier_" in content:
                    self.issues.append(
                        f"⚠️  {file_name} redefines tier methods (should import from aurora_core)")
                else:
                    self.recommendations.append(
                        f"💡 {file_name} might need to import from aurora_core")

    def identify_legacy_files(self):
        """Identify legacy/debug files that should be archived"""
        print("\n🔍 Identifying Legacy Files...")

        legacy_patterns = [
            r"aurora_debug_.*\.py",
            r"aurora_device_demo.*\.py",
            r".*_test\.py",
            r".*_broken\.py",
        ]

        legacy_files = []
        for pattern in legacy_patterns:
            for file in self.root.glob("*.py"):
                if re.match(pattern, file.name):
                    size_kb = file.stat().st_size / 1024
                    legacy_files.append((file.name, size_kb))

        if legacy_files:
            self.recommendations.append(
                f"💡 Found {len(legacy_files)} legacy files ready for archival:")
            for name, size in sorted(legacy_files):
                self.recommendations.append(f"   - {name} ({size:.1f} KB)")
        else:
            self.successes.append("✅ No legacy files found in root")

    def verify_config_files(self):
        """Verify configuration files"""
        print("\n🔍 Verifying Configuration Files...")

        configs = {
            ".pylintrc": "Pylint configuration",
            "pyproject.toml": "Python project config",
            "alembic.ini": "Database migrations",
            "aurora_server_config.json": "Aurora server config",
        }

        for file, description in configs.items():
            path = self.root / file
            if path.exists():
                self.successes.append(f"✅ {file} found ({description})")

    def verify_documentation(self):
        """Verify key documentation exists"""
        print("\n🔍 Verifying Documentation...")

        docs = [
            "AURORA_COMMANDS.md",
            "AURORA_MILESTONE_LOG.md",
            "AURORA_ARCHITECTURE_ANALYSIS.md",
            "AURORA_READY_FOR_USE.md",
        ]

        found_docs = []
        for doc in docs:
            if (self.root / doc).exists():
                found_docs.append(doc)

        if found_docs:
            self.successes.append(
                f"✅ Found {len(found_docs)} key documentation files")

    def check_imports_consistency(self):
        """Check that files properly import from aurora_core"""
        print("\n🔍 Checking Import Consistency...")

        # Files that should import aurora_core
        should_import = [
            "luminar_nexus_v2.py",
            "aurora_chat_server.py",
            "aurora_intelligence_manager.py",
        ]

        for file_name in should_import:
            path = self.root / file_name
            if path.exists():
                content = path.read_text(encoding="utf-8")
                if "from aurora_core import" in content or "import aurora_core" in content:
                    self.successes.append(
                        f"✅ {file_name} imports from aurora_core")
                else:
                    self.recommendations.append(
                        f"💡 {file_name} might need to import from aurora_core")

    def verify_port_configuration(self):
        """Verify service ports are properly configured"""
        print("\n🔍 Verifying Port Configuration...")

        expected_ports = {
            5000: "Backend API",
            5001: "Bridge Service",
            5002: "Self-Learn Service",
            5173: "Frontend (Vite)",
        }

        # Check if services reference these ports
        service_files = [
            "luminar_nexus_v2.py",
            "aurora_chat_server.py",
            "server/package.json",
        ]

        for file_name in service_files:
            path = self.root / file_name
            if path.exists():
                try:
                    content = path.read_text(encoding="utf-8")
                    ports_found = []
                    for port in expected_ports.keys():
                        if str(port) in content:
                            ports_found.append(port)
                    if ports_found:
                        self.successes.append(
                            f"✅ {file_name} references ports: {ports_found}")
                except:
                    pass

    def generate_report(self):
        """Generate comprehensive verification report"""
        print("\n" + "=" * 80)
        print("🔍 AURORA COMPREHENSIVE SYSTEM VERIFICATION")
        print("=" * 80)

        # Run all verifications
        self.verify_core_structure()
        self.verify_service_files()
        self.verify_tools_organization()
        self.verify_frontend_structure()
        self.verify_backend_structure()
        self.check_duplicate_tiers()
        self.identify_legacy_files()
        self.verify_config_files()
        self.verify_documentation()
        self.check_imports_consistency()
        self.verify_port_configuration()

        # Print results
        print("\n" + "=" * 80)
        print("✅ SUCCESSES")
        print("=" * 80)
        for success in self.successes:
            print(success)

        if self.issues:
            print("\n" + "=" * 80)
            print("❌ ISSUES FOUND")
            print("=" * 80)
            for issue in self.issues:
                print(issue)

        if self.recommendations:
            print("\n" + "=" * 80)
            print("💡 RECOMMENDATIONS")
            print("=" * 80)
            for rec in self.recommendations:
                print(rec)

        # Summary
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"✅ Successes: {len(self.successes)}")
        print(f"❌ Issues: {len(self.issues)}")
        print(f"💡 Recommendations: {len(self.recommendations)}")

        # Save report
        report = {
            "timestamp": "2025-11-15",
            "successes": self.successes,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "summary": {
                "total_successes": len(self.successes),
                "total_issues": len(self.issues),
                "total_recommendations": len(self.recommendations),
            },
        }

        report_file = self.root / "AURORA_VERIFICATION_REPORT.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Full report saved to: {report_file}")

        # Overall status
        if len(self.issues) == 0:
            print(
                "\n🎉 SYSTEM STATUS: ✅ ALL CHECKS PASSED - EVERYTHING IS WHERE IT BELONGS")
        elif len(self.issues) <= 3:
            print("\n⚠️  SYSTEM STATUS: MOSTLY ORGANIZED - FEW MINOR ISSUES TO ADDRESS")
        else:
            print("\n🔧 SYSTEM STATUS: NEEDS ORGANIZATION - MULTIPLE ISSUES FOUND")

        return len(self.issues) == 0


if __name__ == "__main__":
    print("\n🚀 Starting Aurora Comprehensive System Verification...")
    print("=" * 80)

    verifier = AuroraSystemVerification()
    all_good = verifier.generate_report()

    print("\n" + "=" * 80)
    print("🔍 Verification Complete!")
    print("=" * 80 + "\n")

    exit(0 if all_good else 1)
