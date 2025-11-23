
#!/usr/bin/env python3
"""
Aurora Comprehensive Repository Analyzer
Analyzes all branches, commits, staged/unstaged changes, and provides self-improvement recommendations
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import hashlib


class AuroraComprehensiveAnalyzer:
    def __init__(self):
        self.project_root = Path(".")
        self.analysis = {
            "timestamp": datetime.now().isoformat(),
            "branches": {
                "local": [],
                "remote": [],
                "active": None
            },
            "commits": {
                "all_commits": [],
                "by_branch": {}
            },
            "changes": {
                "staged": [],
                "unstaged": [],
                "untracked": [],
                "by_branch": {}
            },
            "current_state": {
                "files": [],
                "capabilities": [],
                "systems": []
            },
            "gaps_identified": [],
            "recommendations": []
        }

    def run_git_command(self, cmd):
        """Execute git command and return output"""
        try:
            result = subprocess.run(
                ["git"] + cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:
            print(f"Git command error: {e}")
            return None

    def analyze_all_branches(self):
        """Analyze all local and remote branches"""
        print("🔍 Analyzing all branches...")
        
        # Get current branch
        current = self.run_git_command(["branch", "--show-current"])
        self.analysis["branches"]["active"] = current
        
        # Get all local branches
        local_branches = self.run_git_command(["branch", "--format=%(refname:short)"])
        if local_branches:
            self.analysis["branches"]["local"] = local_branches.split("\n")
        
        # Get all remote branches
        remote_branches = self.run_git_command(["branch", "-r", "--format=%(refname:short)"])
        if remote_branches:
            self.analysis["branches"]["remote"] = [
                b for b in remote_branches.split("\n") 
                if b and "HEAD" not in b
            ]
        
        print(f"  ✅ Found {len(self.analysis['branches']['local'])} local branches")
        print(f"  ✅ Found {len(self.analysis['branches']['remote'])} remote branches")

    def analyze_all_commits(self):
        """Analyze all commits across all branches"""
        print("\n📜 Analyzing all commits...")
        
        all_branches = self.analysis["branches"]["local"] + self.analysis["branches"]["remote"]
        
        for branch in all_branches:
            # Get commits for this branch
            commits_output = self.run_git_command([
                "log",
                branch,
                "--pretty=format:%H|%an|%ae|%ad|%s",
                "--date=iso",
                "-100"  # Last 100 commits per branch
            ])
            
            if commits_output:
                commits = []
                for line in commits_output.split("\n"):
                    if line:
                        parts = line.split("|")
                        if len(parts) >= 5:
                            commits.append({
                                "hash": parts[0],
                                "author": parts[1],
                                "email": parts[2],
                                "date": parts[3],
                                "message": parts[4]
                            })
                
                self.analysis["commits"]["by_branch"][branch] = commits
                self.analysis["commits"]["all_commits"].extend(commits)
        
        # Remove duplicates
        unique_commits = {}
        for commit in self.analysis["commits"]["all_commits"]:
            unique_commits[commit["hash"]] = commit
        self.analysis["commits"]["all_commits"] = list(unique_commits.values())
        
        print(f"  ✅ Analyzed {len(self.analysis['commits']['all_commits'])} unique commits")

    def analyze_changes_per_branch(self):
        """Analyze staged/unstaged changes for each branch"""
        print("\n🔄 Analyzing changes per branch...")
        
        original_branch = self.analysis["branches"]["active"]
        
        for branch in self.analysis["branches"]["local"]:
            # Checkout branch
            self.run_git_command(["checkout", branch])
            
            # Get staged files
            staged = self.run_git_command(["diff", "--cached", "--name-status"])
            staged_files = []
            if staged:
                for line in staged.split("\n"):
                    if line:
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            staged_files.append({
                                "status": parts[0],
                                "file": parts[1]
                            })
            
            # Get unstaged files
            unstaged = self.run_git_command(["diff", "--name-status"])
            unstaged_files = []
            if unstaged:
                for line in unstaged.split("\n"):
                    if line:
                        parts = line.split("\t")
                        if len(parts) >= 2:
                            unstaged_files.append({
                                "status": parts[0],
                                "file": parts[1]
                            })
            
            # Get untracked files
            untracked = self.run_git_command(["ls-files", "--others", "--exclude-standard"])
            untracked_files = untracked.split("\n") if untracked else []
            
            self.analysis["changes"]["by_branch"][branch] = {
                "staged": staged_files,
                "unstaged": unstaged_files,
                "untracked": untracked_files
            }
            
            if staged_files or unstaged_files or untracked_files:
                print(f"  ⚠️  {branch}: {len(staged_files)} staged, {len(unstaged_files)} unstaged, {len(untracked_files)} untracked")
        
        # Restore original branch
        if original_branch:
            self.run_git_command(["checkout", original_branch])

    def analyze_current_state(self):
        """Analyze Aurora's current capabilities and systems"""
        print("\n🤖 Analyzing Aurora's current state...")
        
        # Scan Python files
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if "venv" not in str(f) and "node_modules" not in str(f)]
        
        # Scan TypeScript/React files
        ts_files = list(self.project_root.rglob("*.ts")) + list(self.project_root.rglob("*.tsx"))
        ts_files = [f for f in ts_files if "node_modules" not in str(f)]
        
        self.analysis["current_state"]["files"] = {
            "python": len(python_files),
            "typescript": len(ts_files),
            "total": len(python_files) + len(ts_files)
        }
        
        # Identify capability files
        capabilities = []
        for py_file in python_files:
            name = py_file.name.lower()
            if any(kw in name for kw in ["aurora", "autonomous", "intelligence", "learning", "engine"]):
                capabilities.append(str(py_file.relative_to(self.project_root)))
        
        self.analysis["current_state"]["capabilities"] = capabilities
        
        # Identify system files
        systems = []
        for py_file in python_files:
            name = py_file.name.lower()
            if any(kw in name for kw in ["manager", "orchestrator", "nexus", "bridge", "daemon"]):
                systems.append(str(py_file.relative_to(self.project_root)))
        
        self.analysis["current_state"]["systems"] = systems
        
        print(f"  ✅ Found {len(capabilities)} capability modules")
        print(f"  ✅ Found {len(systems)} system modules")

    def compare_and_identify_gaps(self):
        """Compare branches and identify what's missing in current state"""
        print("\n🔍 Comparing branches and identifying gaps...")
        
        current_branch = self.analysis["branches"]["active"]
        gaps = []
        
        # Compare commits - find features in other branches not in current
        current_commits = set()
        if current_branch in self.analysis["commits"]["by_branch"]:
            current_commits = {c["hash"] for c in self.analysis["commits"]["by_branch"][current_branch]}
        
        for branch, commits in self.analysis["commits"]["by_branch"].items():
            if branch != current_branch:
                for commit in commits:
                    if commit["hash"] not in current_commits:
                        # Check if commit message indicates a feature
                        msg = commit["message"].lower()
                        if any(kw in msg for kw in ["add", "implement", "create", "feature", "new"]):
                            gaps.append({
                                "type": "missing_commit",
                                "branch": branch,
                                "commit": commit["hash"][:8],
                                "message": commit["message"],
                                "severity": "medium"
                            })
        
        # Compare file changes
        for branch, changes in self.analysis["changes"]["by_branch"].items():
            if branch != current_branch:
                for staged_file in changes["staged"]:
                    gaps.append({
                        "type": "uncommitted_change",
                        "branch": branch,
                        "file": staged_file["file"],
                        "status": staged_file["status"],
                        "severity": "high"
                    })
        
        self.analysis["gaps_identified"] = gaps
        print(f"  ✅ Identified {len(gaps)} gaps")

    def generate_recommendations(self):
        """Generate specific recommendations for Aurora's improvement"""
        print("\n💡 Generating improvement recommendations...")
        
        recommendations = []
        
        # 1. Check for uncommitted changes
        uncommitted = [g for g in self.analysis["gaps_identified"] if g["type"] == "uncommitted_change"]
        if uncommitted:
            recommendations.append({
                "priority": "HIGH",
                "category": "Code Integration",
                "issue": f"{len(uncommitted)} uncommitted changes found in other branches",
                "recommendation": "Review and merge uncommitted changes from other branches",
                "action": "Run cross-branch scanner and merge valuable changes"
            })
        
        # 2. Check for missing features
        missing_commits = [g for g in self.analysis["gaps_identified"] if g["type"] == "missing_commit"]
        if missing_commits:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Feature Parity",
                "issue": f"{len(missing_commits)} features exist in other branches",
                "recommendation": "Cherry-pick or merge features from other branches",
                "action": "Review commit messages and selectively integrate features"
            })
        
        # 3. Check capability coverage
        total_capabilities = len(self.analysis["current_state"]["capabilities"])
        if total_capabilities < 50:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Capability Expansion",
                "issue": f"Only {total_capabilities} capability modules found",
                "recommendation": "Expand Aurora's capability modules to cover more domains",
                "action": "Create new capability modules for missing domains"
            })
        
        # 4. Check system integration
        total_systems = len(self.analysis["current_state"]["systems"])
        if total_systems < 20:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "System Architecture",
                "issue": f"Only {total_systems} system modules found",
                "recommendation": "Add more orchestration and management systems",
                "action": "Create unified orchestrator to connect existing systems"
            })
        
        # 5. Check for untracked files across branches
        untracked_count = sum(
            len(changes["untracked"]) 
            for changes in self.analysis["changes"]["by_branch"].values()
        )
        if untracked_count > 10:
            recommendations.append({
                "priority": "LOW",
                "category": "Repository Hygiene",
                "issue": f"{untracked_count} untracked files across branches",
                "recommendation": "Review and either commit or add to .gitignore",
                "action": "Clean up untracked files to maintain repository cleanliness"
            })
        
        # 6. Branch consolidation
        if len(self.analysis["branches"]["local"]) > 10:
            recommendations.append({
                "priority": "LOW",
                "category": "Branch Management",
                "issue": f"{len(self.analysis['branches']['local'])} local branches exist",
                "recommendation": "Consolidate or archive inactive branches",
                "action": "Merge valuable branches and delete stale ones"
            })
        
        self.analysis["recommendations"] = recommendations
        print(f"  ✅ Generated {len(recommendations)} recommendations")

    def save_analysis(self):
        """Save analysis to file"""
        output_file = self.project_root / "AURORA_COMPREHENSIVE_ANALYSIS.json"
        with open(output_file, "w") as f:
            json.dump(self.analysis, f, indent=2)
        print(f"\n💾 Analysis saved to {output_file}")
        return output_file

    def generate_report(self):
        """Generate human-readable report"""
        report_file = self.project_root / "AURORA_SELF_IMPROVEMENT_PLAN.md"
        
        with open(report_file, "w") as f:
            f.write("# 🌟 Aurora Self-Improvement Analysis Report\n\n")
            f.write(f"**Generated:** {self.analysis['timestamp']}\n\n")
            f.write("---\n\n")
            
            # Summary
            f.write("## 📊 Repository Summary\n\n")
            f.write(f"- **Active Branch:** `{self.analysis['branches']['active']}`\n")
            f.write(f"- **Local Branches:** {len(self.analysis['branches']['local'])}\n")
            f.write(f"- **Remote Branches:** {len(self.analysis['branches']['remote'])}\n")
            f.write(f"- **Total Commits Analyzed:** {len(self.analysis['commits']['all_commits'])}\n")
            f.write(f"- **Gaps Identified:** {len(self.analysis['gaps_identified'])}\n\n")
            
            # Current State
            f.write("## 🤖 Current State Analysis\n\n")
            f.write(f"- **Python Files:** {self.analysis['current_state']['files']['python']}\n")
            f.write(f"- **TypeScript Files:** {self.analysis['current_state']['files']['typescript']}\n")
            f.write(f"- **Capability Modules:** {len(self.analysis['current_state']['capabilities'])}\n")
            f.write(f"- **System Modules:** {len(self.analysis['current_state']['systems'])}\n\n")
            
            # Gaps
            f.write("## 🔍 Identified Gaps\n\n")
            if self.analysis['gaps_identified']:
                for i, gap in enumerate(self.analysis['gaps_identified'][:20], 1):
                    f.write(f"### {i}. {gap['type'].replace('_', ' ').title()}\n")
                    f.write(f"- **Branch:** `{gap['branch']}`\n")
                    if 'file' in gap:
                        f.write(f"- **File:** `{gap['file']}`\n")
                    if 'message' in gap:
                        f.write(f"- **Message:** {gap['message']}\n")
                    f.write(f"- **Severity:** {gap['severity'].upper()}\n\n")
            else:
                f.write("No gaps identified. Aurora is in sync!\n\n")
            
            # Recommendations
            f.write("## 💡 Improvement Recommendations\n\n")
            for i, rec in enumerate(self.analysis['recommendations'], 1):
                f.write(f"### {i}. {rec['category']} [{rec['priority']}]\n\n")
                f.write(f"**Issue:** {rec['issue']}\n\n")
                f.write(f"**Recommendation:** {rec['recommendation']}\n\n")
                f.write(f"**Action Required:** {rec['action']}\n\n")
                f.write("---\n\n")
            
            # Priority Actions
            f.write("## 🎯 Priority Actions\n\n")
            high_priority = [r for r in self.analysis['recommendations'] if r['priority'] == 'HIGH']
            if high_priority:
                f.write("### Immediate Actions Required:\n\n")
                for rec in high_priority:
                    f.write(f"- [ ] **{rec['category']}:** {rec['action']}\n")
                f.write("\n")
            
            medium_priority = [r for r in self.analysis['recommendations'] if r['priority'] == 'MEDIUM']
            if medium_priority:
                f.write("### Short-term Improvements:\n\n")
                for rec in medium_priority:
                    f.write(f"- [ ] **{rec['category']}:** {rec['action']}\n")
                f.write("\n")
            
            low_priority = [r for r in self.analysis['recommendations'] if r['priority'] == 'LOW']
            if low_priority:
                f.write("### Long-term Enhancements:\n\n")
                for rec in low_priority:
                    f.write(f"- [ ] **{rec['category']}:** {rec['action']}\n")
                f.write("\n")
            
            f.write("---\n\n")
            f.write("**Next Steps:** Review this report and prioritize actions based on urgency and impact.\n")
        
        print(f"📄 Report saved to {report_file}")
        return report_file

    def run_complete_analysis(self):
        """Run the complete analysis"""
        print("=" * 70)
        print("🌌 AURORA COMPREHENSIVE REPOSITORY ANALYZER")
        print("=" * 70)
        
        self.analyze_all_branches()
        self.analyze_all_commits()
        self.analyze_changes_per_branch()
        self.analyze_current_state()
        self.compare_and_identify_gaps()
        self.generate_recommendations()
        
        json_file = self.save_analysis()
        report_file = self.generate_report()
        
        print("\n" + "=" * 70)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 70)
        print(f"\n📊 JSON Analysis: {json_file}")
        print(f"📄 Improvement Plan: {report_file}")
        print(f"\n🎯 Total Recommendations: {len(self.analysis['recommendations'])}")
        
        high = len([r for r in self.analysis['recommendations'] if r['priority'] == 'HIGH'])
        medium = len([r for r in self.analysis['recommendations'] if r['priority'] == 'MEDIUM'])
        low = len([r for r in self.analysis['recommendations'] if r['priority'] == 'LOW'])
        
        print(f"   - HIGH Priority: {high}")
        print(f"   - MEDIUM Priority: {medium}")
        print(f"   - LOW Priority: {low}")
        print("\n" + "=" * 70)


if __name__ == "__main__":
    analyzer = AuroraComprehensiveAnalyzer()
    analyzer.run_complete_analysis()
