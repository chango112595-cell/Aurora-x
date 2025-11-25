"""
Aurora Deep System Scan - Find ALL Capabilities
Scan entire system including git history, unused files, tools/, etc.
Check if "missing" capabilities actually exist
"""

from aurora_core from typing import Dict, List, Tuple, Optional, Any, Union
import AuroraCoreIntelligence
import sys
import os
from pathlib import Path
import subprocess
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class AuroraDeepScanner:
    def __init__(self, aurora_core: AuroraCoreIntelligence):
        self.aurora = aurora_core
        self.project_root = aurora_core.project_root
        self.findings = {
            "claimed_missing": [],
            "found_in_system": [],
            "git_history": [],
            "unused_modules": [],
            "hidden_capabilities": []
        }

    def scan_for_capability(self, capability_name: str, keywords: list) -> dict:
        """Search entire system for a specific capability"""
        result = {
            "capability": capability_name,
            "keywords": keywords,
            "found_in_files": [],
            "found_in_git": False,
            "git_commits": [],
            "status": "NOT FOUND"
        }

        # Search all Python files
        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                content_lower = content.lower()

                matches = [kw for kw in keywords if kw.lower()
                           in content_lower]
                if matches:
                    result["found_in_files"].append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "matched_keywords": matches
                    })
            except Exception:
                pass

        # Search git history
        try:
            git_log = subprocess.run(
                ['git', 'log', '--all', '--oneline',
                    '--grep=' + '|'.join(keywords)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if git_log.stdout.strip():
                result["found_in_git"] = True
                result["git_commits"] = git_log.stdout.strip().split('\n')[:5]
        except Exception:
            pass

        if result["found_in_files"] or result["found_in_git"]:
            result["status"] = "FOUND"

        return result

    def scan_all_claimed_gaps(self):
        """Scan for all 79 capabilities Aurora claims are missing"""
        print("[SCAN] Deep scanning for claimed missing capabilities...\n")

        gaps = [
            {
                "name": "Autonomous Initiative / Proactive Daemon",
                "keywords": ["proactive", "daemon", "background", "monitor", "continuous", "initiative"]
            },
            {
                "name": "Real-time Code Understanding / AST",
                "keywords": ["ast", "tree-sitter", "parser", "symbol", "dependency graph", "index"]
            },
            {
                "name": "Automated Testing & Validation",
                "keywords": ["pytest", "test generation", "automated test", "test runner", "validation"]
            },
            {
                "name": "Git Integration & Safety",
                "keywords": ["git commit", "git branch", "rollback", "version control", "git integration"]
            },
            {
                "name": "Contextual Awareness / Long-term Memory",
                "keywords": ["vector", "embedding", "long-term memory", "preference", "context memory"]
            },
            {
                "name": "Multi-file Refactoring",
                "keywords": ["refactor", "multi-file", "rename", "extract", "cross-file"]
            },
            {
                "name": "Performance Optimization",
                "keywords": ["profile", "optimize", "performance", "bottleneck", "benchmark"]
            },
            {
                "name": "Advanced NLU",
                "keywords": ["semantic", "intent", "dialogue", "nlu", "understanding"]
            },
            {
                "name": "Learning & Adaptation",
                "keywords": ["reinforcement", "learning", "adapt", "feedback", "improve"]
            },
            {
                "name": "Integration Ecosystem",
                "keywords": ["github api", "integration", "mcp", "api client", "webhook"]
            }
        ]

        for gap in gaps:
            print(f"Scanning for: {gap['name']}")
            result = self.scan_for_capability(gap['name'], gap['keywords'])

            if result["status"] == "FOUND":
                print(f"  [OK] FOUND! In {len(result['found_in_files'])} files")
                self.findings["found_in_system"].append(result)
            else:
                print(f"  [ERROR] Not found")
                self.findings["claimed_missing"].append(result)
            print()

    def scan_unused_modules(self):
        """Find modules that exist but might not be used"""
        print("[SCAN] Scanning for unused/dormant modules...\n")

        # Check tools/ directory
        tools_dir = self.project_root / "tools"
        if tools_dir.exists():
            tool_files = list(tools_dir.glob("aurora_*.py"))
            print(f"Found {len(tool_files)} tool files in tools/")

            # Check which are imported in main system
            core_file = self.project_root / "aurora_core.py"
            core_content = core_file.read_text(encoding='utf-8')

            unused = []
            for tool in tool_files:
                tool_name = tool.stem
                if tool_name not in core_content:
                    unused.append(tool_name)

            print(f"Unused tools: {len(unused)}")
            self.findings["unused_modules"] = unused[:20]  # Show first 20

        print()

    def scan_git_history_for_removed_features(self):
        """Check git history for features that were removed"""
        print("[SCAN] Checking git history for removed capabilities...\n")

        try:
            # Get list of deleted files
            deleted = subprocess.run(
                ['git', 'log', '--diff-filter=D', '--summary', '--oneline'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if deleted.stdout:
                lines = deleted.stdout.split('\n')
                deleted_files = [l.strip()
                                 for l in lines if 'delete mode' in l.lower()]
                print(f"Found {len(deleted_files)} deleted files in history")
                self.findings["git_history"] = deleted_files[:10]
        except Exception as e:
            print(f"Git history scan failed: {e}")

        print()

    def find_hidden_capabilities(self):
        """Find capabilities in comments, docstrings, TODO markers"""
        print("[SCAN] Searching for hidden/commented capabilities...\n")

        hidden = []

        for py_file in self.project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Look for TODO, FIXME, NOTE comments
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if any(marker in line.upper() for marker in ['TODO', 'FIXME', 'NOTE', 'FUTURE']):
                        if any(word in line.lower() for word in ['autonomous', 'proactive', 'learning', 'improvement']):
                            hidden.append({
                                "file": str(py_file.relative_to(self.project_root)),
                                "line": i,
                                "content": line.strip()[:100]
                            })
            except Exception:
                pass

        print(f"Found {len(hidden)} hidden capability markers")
        self.findings["hidden_capabilities"] = hidden[:15]
        print()

    def generate_report(self) -> str:
        """Generate comprehensive report"""
        report = []
        report.append("=" * 80)
        report.append("AURORA DEEP SYSTEM SCAN REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append(f"Project Root: {self.project_root}")
        report.append("")

        # Summary
        report.append("SUMMARY:")
        report.append("-" * 80)
        report.append(
            f"Capabilities Aurora thinks are missing: {len(self.findings['claimed_missing'])}")
        report.append(
            f"Capabilities actually FOUND in system: {len(self.findings['found_in_system'])}")
        report.append(
            f"Unused modules discovered: {len(self.findings['unused_modules'])}")
        report.append(
            f"Hidden capability markers: {len(self.findings['hidden_capabilities'])}")
        report.append("")

        # Found capabilities (Aurora thinks they're missing but they EXIST!)
        if self.findings["found_in_system"]:
            report.append("=" * 80)
            report.append(
                "CAPABILITIES FOUND (Aurora didn't know she had these!):")
            report.append("=" * 80)

            for cap in self.findings["found_in_system"]:
                report.append(f"\n[OK] {cap['capability']}")
                report.append(f"   Status: {cap['status']}")
                report.append(
                    f"   Found in {len(cap['found_in_files'])} files:")

                for file_info in cap['found_in_files'][:5]:
                    report.append(f"      {file_info['file']}")
                    report.append(
                        f"       Keywords: {', '.join(file_info['matched_keywords'])}")

                if cap['found_in_git']:
                    report.append(
                        f"   Git history: {len(cap['git_commits'])} relevant commits")
                report.append("")

        # Actually missing
        if self.findings["claimed_missing"]:
            report.append("=" * 80)
            report.append("CAPABILITIES TRULY MISSING:")
            report.append("=" * 80)

            for cap in self.findings["claimed_missing"]:
                report.append(f"\n[ERROR] {cap['capability']}")
                report.append(f"   Searched for: {', '.join(cap['keywords'])}")
                report.append(
                    f"   Status: NOT FOUND in codebase or git history")
                report.append("")

        # Unused modules
        if self.findings["unused_modules"]:
            report.append("=" * 80)
            report.append("UNUSED/DORMANT MODULES (exist but not integrated):")
            report.append("=" * 80)

            for module in self.findings["unused_modules"]:
                report.append(f"   {module}")
            report.append("")
            report.append(
                f"These {len(self.findings['unused_modules'])} modules exist but aren't imported in aurora_core.py")
            report.append("")

        # Hidden capabilities
        if self.findings["hidden_capabilities"]:
            report.append("=" * 80)
            report.append("HIDDEN CAPABILITIES (in comments/TODOs):")
            report.append("=" * 80)

            for hidden in self.findings["hidden_capabilities"]:
                report.append(
                    f"\n  File: {hidden['file']} (line {hidden['line']})")
                report.append(f"  {hidden['content']}")
            report.append("")

        report.append("=" * 80)
        report.append("CONCLUSION:")
        report.append("=" * 80)

        found_count = len(self.findings["found_in_system"])
        missing_count = len(self.findings["claimed_missing"])

        if found_count > missing_count:
            report.append("\n[TARGET] AURORA HAS MORE THAN SHE THINKS!")
            report.append(
                f"   She found {found_count} 'missing' capabilities that actually EXIST.")
            report.append(
                "   Problem: Capabilities exist but Aurora doesn't know about them.")
            report.append(
                "   Solution: Improve self-awareness and module discovery.")
        elif missing_count > found_count:
            report.append("\n[WARN]  CAPABILITIES ARE TRULY MISSING")
            report.append(f"   {missing_count} claimed gaps are real.")
            report.append("   These need to be built from scratch.")
        else:
            report.append("\n[OK] ACCURATE SELF-ASSESSMENT")
            report.append(
                "   Aurora correctly identified what she has and lacks.")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    print("=" * 80)
    print("AURORA DEEP SYSTEM SCAN")
    print("Checking if 'missing' capabilities actually exist in the system")
    print("=" * 80)
    print()

    # Initialize Aurora
    print("Initializing Aurora...")
    aurora = AuroraCoreIntelligence()
    print("[OK] Aurora initialized\n")

    # Create scanner
    scanner = AuroraDeepScanner(aurora)

    # Run all scans
    scanner.scan_all_claimed_gaps()
    scanner.scan_unused_modules()
    scanner.scan_git_history_for_removed_features()
    scanner.find_hidden_capabilities()

    # Generate report
    print("\n" + "=" * 80)
    print("GENERATING COMPREHENSIVE REPORT")
    print("=" * 80)
    print()

    report = scanner.generate_report()
    print(report)

    # Save report
    report_file = Path(__file__).parent / "AURORA_DEEP_SCAN_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n[EMOJI] Full report saved to: {report_file}")

    # Save JSON data
    json_file = Path(__file__).parent / "aurora_deep_scan_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(scanner.findings, f, indent=2)

    print(f"[EMOJI] Raw data saved to: {json_file}")


if __name__ == "__main__":
    main()
