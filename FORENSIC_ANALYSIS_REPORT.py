#!/usr/bin/env python3
"""
AURORA FORENSIC ANALYSIS - COMPREHENSIVE DEEP DIVE
Systematic analysis of every system component with issue identification
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any


class AuroraForensicAnalyzer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.info = []

    def log_issue(self, category: str, severity: str, description: str, file: str = None):
        """Log an issue found during analysis"""
        issue = {
            "category": category,
            "severity": severity,  # CRITICAL, HIGH, MEDIUM, LOW
            "description": description,
            "file": file
        }

        if severity == "CRITICAL":
            self.issues.append(issue)
        elif severity in ["HIGH", "MEDIUM"]:
            self.warnings.append(issue)
        else:
            self.info.append(issue)

    def analyze_typescript_paths(self):
        """Check if TypeScript path mappings are correct"""
        print("\n[ANALYSIS] TypeScript Path Configuration")
        print("━" * 60)

        tsconfig = self.project_root / "tsconfig.json"
        if not tsconfig.exists():
            self.log_issue("TypeScript", "CRITICAL", "tsconfig.json missing")
            return

        with open(tsconfig) as f:
            config = json.load(f)

        # Check if @shared path is defined
        paths = config.get("compilerOptions", {}).get("paths", {})
        if "@shared/*" not in paths:
            self.log_issue(
                "TypeScript",
                "CRITICAL",
                "@shared/* path mapping missing in tsconfig.json",
                str(tsconfig)
            )
            print("  ✗ Missing @shared/* path mapping")
        else:
            print(f"  ✓ @shared/* mapped to: {paths['@shared/*']}")

        # Check if @/* mapping points to correct location
        if "@/*" in paths:
            client_path = paths["@/*"][0]
            print(f"  ✓ @/* mapped to: {client_path}")

            # Verify the path exists
            actual_path = self.project_root / client_path.replace("./*", "")
            if not actual_path.exists():
                self.log_issue(
                    "TypeScript",
                    "HIGH",
                    f"@/* maps to non-existent path: {client_path}",
                    str(tsconfig)
                )

    def analyze_imports(self):
        """Analyze import statements for missing modules"""
        print("\n[ANALYSIS] Import Dependencies")
        print("━" * 60)

        # Check for @shared/schema usage
        shared_schema = self.project_root / "shared" / "schema.ts"
        if not shared_schema.exists():
            self.log_issue(
                "Dependencies",
                "CRITICAL",
                "shared/schema.ts exists but not in TypeScript paths",
                str(shared_schema)
            )
            print("  ✗ shared/schema.ts found but @shared/* not configured")
        else:
            print(f"  ✓ shared/schema.ts exists")

        # Check for React Router usage without package
        client_files = list(
            (self.project_root / "client" / "src").rglob("*.tsx"))
        uses_use_location = False

        for file in client_files:
            try:
                content = file.read_text(encoding='utf-8')
                if 'useLocation' in content and 'from' not in content:
                    uses_use_location = True
                    self.log_issue(
                        "Dependencies",
                        "CRITICAL",
                        f"useLocation used without import in {file.name}",
                        str(file)
                    )
                    print(
                        f"  ✗ {file.name}: useLocation without proper import")
            except Exception as e:
                pass

    def analyze_python_core(self):
        """Analyze Python core for runtime issues"""
        print("\n[ANALYSIS] Python Core Integrity")
        print("━" * 60)

        aurora_core = self.project_root / "aurora_core.py"
        if not aurora_core.exists():
            self.log_issue("Python", "CRITICAL", "aurora_core.py missing")
            return

        # Test import
        try:
            sys.path.insert(0, str(self.project_root))
            from aurora_core import AuroraCoreIntelligence

            # Test initialization
            aurora = AuroraCoreIntelligence()

            # Check attributes
            if hasattr(aurora, 'total_power'):
                print(f"  ✓ total_power: {aurora.total_power}")
            else:
                self.log_issue("Python", "HIGH",
                               "total_power attribute missing")

            if hasattr(aurora, 'knowledge_units'):
                print(f"  ✓ knowledge_units: {aurora.knowledge_units}")
            else:
                self.log_issue("Python", "MEDIUM",
                               "knowledge_units attribute missing")

            print("  ✓ aurora_core.py imports successfully")

        except Exception as e:
            self.log_issue("Python", "CRITICAL",
                           f"aurora_core.py import failed: {str(e)}")
            print(f"  ✗ Import error: {str(e)}")

    def analyze_architecture(self):
        """Analyze active vs legacy architecture"""
        print("\n[ANALYSIS] Architecture & Active Components")
        print("━" * 60)

        # Check Next.js API route
        next_api = self.project_root / "app" / "api" / "chat" / "route.ts"
        if next_api.exists():
            print("  ✓ Next.js API route (app/api/chat/route.ts) - ACTIVE")
        else:
            self.log_issue("Architecture", "CRITICAL",
                           "Next.js API route missing")

        # Check server bridge
        bridge = self.project_root / "server" / "aurora-chat.ts"
        if bridge.exists():
            print("  ✓ Python bridge (server/aurora-chat.ts) - ACTIVE")
        else:
            self.log_issue("Architecture", "CRITICAL", "Python bridge missing")

        # Check legacy Express server
        express_server = self.project_root / "server" / "index.ts"
        if express_server.exists():
            print("  ⚠ Legacy Express server exists but not used")
            self.log_issue(
                "Architecture",
                "LOW",
                "Legacy Express server (server/index.ts) still present",
                str(express_server)
            )

    def analyze_build_config(self):
        """Analyze build configuration"""
        print("\n[ANALYSIS] Build Configuration")
        print("━" * 60)

        # Check Next.js config
        next_config = self.project_root / "next.config.mjs"
        if next_config.exists():
            print("  ✓ next.config.mjs exists")
        else:
            self.log_issue("Build", "HIGH", "next.config.mjs missing")

        # Check package.json scripts
        pkg_json = self.project_root / "package.json"
        if pkg_json.exists():
            with open(pkg_json) as f:
                pkg = json.load(f)

            scripts = pkg.get("scripts", {})
            required_scripts = ["dev", "build", "start"]

            for script in required_scripts:
                if script in scripts:
                    print(f"  ✓ Script '{script}': {scripts[script]}")
                else:
                    self.log_issue("Build", "MEDIUM",
                                   f"Missing npm script: {script}")

    def analyze_runtime_state(self):
        """Analyze current runtime state"""
        print("\n[ANALYSIS] Runtime State")
        print("━" * 60)

        # Check if services are running (via port check)
        try:
            import socket
            ports_to_check = [5000, 5001, 5002, 5173]
            active_ports = []

            for port in ports_to_check:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()

                if result == 0:
                    active_ports.append(port)
                    print(f"  ✓ Port {port}: ACTIVE")
                else:
                    print(f"  ✗ Port {port}: INACTIVE")

            if len(active_ports) == 0:
                self.log_issue("Runtime", "HIGH",
                               "No services running on expected ports")
            elif 5000 not in active_ports:
                self.log_issue("Runtime", "HIGH",
                               "Main Next.js service (port 5000) not running")

        except Exception as e:
            print(f"  ⚠ Could not check ports: {str(e)}")

    def generate_report(self):
        """Generate final forensic report"""
        print("\n" + "=" * 60)
        print("FORENSIC ANALYSIS COMPLETE")
        print("=" * 60)

        total_issues = len(self.issues) + len(self.warnings) + len(self.info)

        print(f"\nTotal findings: {total_issues}")
        print(
            f"  CRITICAL issues: {len([i for i in self.issues if i['severity'] == 'CRITICAL'])}")
        print(
            f"  HIGH issues: {len([i for i in self.warnings if i['severity'] == 'HIGH'])}")
        print(
            f"  MEDIUM issues: {len([i for i in self.warnings if i['severity'] == 'MEDIUM'])}")
        print(
            f"  LOW issues: {len([i for i in self.info if i['severity'] == 'LOW'])}")

        if self.issues:
            print("\n🔴 CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"\n  [{issue['category']}] {issue['description']}")
                if issue['file']:
                    print(f"    File: {issue['file']}")

        if self.warnings:
            print("\n⚠️  HIGH/MEDIUM ISSUES:")
            for issue in self.warnings:
                print(f"\n  [{issue['category']}] {issue['description']}")
                if issue['file']:
                    print(f"    File: {issue['file']}")

        # Save detailed report
        report = {
            "timestamp": str(Path(__file__).stat().st_mtime),
            "total_findings": total_issues,
            "critical_issues": [i for i in self.issues if i['severity'] == 'CRITICAL'],
            "high_issues": [i for i in self.warnings if i['severity'] == 'HIGH'],
            "medium_issues": [i for i in self.warnings if i['severity'] == 'MEDIUM'],
            "low_issues": [i for i in self.info if i['severity'] == 'LOW']
        }

        report_file = self.project_root / "AURORA_FORENSIC_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")

        return len([i for i in self.issues if i['severity'] == 'CRITICAL']) == 0


if __name__ == "__main__":
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║          AURORA FORENSIC ANALYSIS - DEEP DIVE                  ║")
    print("╚════════════════════════════════════════════════════════════════╝")

    analyzer = AuroraForensicAnalyzer()

    analyzer.analyze_typescript_paths()
    analyzer.analyze_imports()
    analyzer.analyze_python_core()
    analyzer.analyze_architecture()
    analyzer.analyze_build_config()
    analyzer.analyze_runtime_state()

    success = analyzer.generate_report()

    sys.exit(0 if success else 1)
