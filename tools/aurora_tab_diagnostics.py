#!/usr/bin/env python3
"""
Aurora Comprehensive Tab Diagnostics
🌟 Autonomous analysis of all UI tabs for issues
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


class AuroraTabDiagnostics:
    """Aurora's comprehensive tab diagnostics engine"""

    def __init__(self):
        self.project_root = Path("/workspaces/Aurora-x")
        self.client_src = self.project_root / "client" / "src"
        self.issues = {}

    def log(self, level: str, message: str):
        """Aurora's logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "🌟", "OK": "✅", "ISSUE": "🐛", "WARN": "⚠️"}
        icon = icons.get(level, "→")
        print(f"[{timestamp}] {icon} Aurora: {message}")

    def analyze_tab(self, tab_name: str, file_path: Path) -> dict[str, Any]:
        """Analyze a single tab for issues"""
        issues = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.log("WARN", f"Could not read {tab_name}: {e}")
            return {"tab": tab_name, "status": "unreadable", "issues": []}

        # Check for API endpoint issues
        if "fetch" in content:
            fetch_calls = re.findall(r'fetch\([\'"]([^\'"]+)[\'"]', content)
            for endpoint in fetch_calls:
                if "404" in content or "error" in content.lower():
                    issues.append({"type": "Potential API endpoint issue", "endpoint": endpoint, "severity": "HIGH"})

        # Check for data display issues
        if "useState" in content and ".map(" in content:
            if "return null" in content or "!data" in content:
                # Check if there's proper fallback UI
                if "loading" not in content.lower() or "<div>" not in content:
                    issues.append({"type": "Missing loading/empty state UI", "severity": "MEDIUM"})

        # Check for connection/polling issues
        if "setInterval" in content or "refetchInterval" in content:
            if "catch" not in content:
                issues.append({"type": "Missing error handling in polling", "severity": "MEDIUM"})

        # Check for routing issues
        if "navigate" in content or "useLocation" in content:
            if "Router" not in content and "Route" not in content:
                issues.append({"type": "Potential routing issue", "severity": "MEDIUM"})

        # Check for real-time data display
        if "real" not in content.lower() and "live" not in content.lower() and "socket" not in content.lower():
            if "Activity" in content or "Status" in content or "Monitor" in content:
                issues.append({"type": "Missing real-time data functionality", "severity": "HIGH"})

        return {
            "tab": tab_name,
            "file": str(file_path.relative_to(self.project_root)),
            "status": "ok" if not issues else "has_issues",
            "issue_count": len(issues),
            "issues": issues,
        }

    def run_diagnostics(self) -> dict[str, Any]:
        """Run diagnostics on all tabs"""
        self.log("INFO", "Starting comprehensive tab diagnostics...")

        tabs_to_check = {
            "Self-Learning": self.client_src / "pages" / "self-learning.tsx",
            "Server Control": self.client_src / "pages" / "server-control.tsx",
            "Luminar Nexus": self.client_src / "pages" / "luminar-nexus.tsx",
            "Comparison": self.client_src / "pages" / "ComparisonDashboard.tsx",
            "Aurora Dashboard": self.client_src / "pages" / "dashboard.tsx",
            "Code Library": self.client_src / "pages" / "library.tsx",
            "Chat": self.client_src / "pages" / "chat.tsx",
        }

        total_issues = 0

        for tab_name, file_path in tabs_to_check.items():
            result = self.analyze_tab(tab_name, file_path)
            self.issues[tab_name] = result

            if result["status"] == "has_issues":
                self.log("ISSUE", f"{tab_name}: {result['issue_count']} issues found")
                total_issues += result["issue_count"]
            else:
                self.log("OK", f"{tab_name}: No issues detected")

        self.log("INFO", f"Total issues found: {total_issues}")

        return {
            "timestamp": datetime.now().isoformat(),
            "total_tabs": len(tabs_to_check),
            "total_issues": total_issues,
            "tabs": self.issues,
        }

    def save_report(self, report: dict[str, Any]):
        """Save diagnostics report"""
        report_path = self.project_root / ".aurora_knowledge" / "tab_diagnostics_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        self.log("OK", f"Report saved to {report_path}")


def main():
    """Aurora's autonomous diagnostics"""

    print("\n" + "=" * 80)
    print("🌟 AURORA COMPREHENSIVE TAB DIAGNOSTICS")
    print("=" * 80 + "\n")

    diagnostics = AuroraTabDiagnostics()
    report = diagnostics.run_diagnostics()
    diagnostics.save_report(report)

    print("\n" + "=" * 80)
    print("DIAGNOSTICS SUMMARY")
    print("=" * 80)
    print(f"Total Tabs Checked: {report['total_tabs']}")
    print(f"Total Issues Found: {report['total_issues']}")
    print("\nDetailed Issues:")
    for tab_name, result in report["tabs"].items():
        if result["status"] == "has_issues":
            print(f"\n{tab_name} ({result['issue_count']} issues):")
            for issue in result["issues"]:
                print(f"  • {issue['type']} [{issue['severity']}]")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
