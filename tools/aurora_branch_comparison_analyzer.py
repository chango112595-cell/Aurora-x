
#!/usr/bin/env python3
"""
Aurora Branch Comparison Analyzer
Compares current state against all branches to find valuable missing features
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class AuroraBranchComparator:
    def __init__(self):
        self.current_branch = self.get_current_branch()
        self.analysis = {
            "timestamp": datetime.now().isoformat(),
            "current_branch": self.current_branch,
            "current_state": {},
            "branch_features": {},
            "missing_features": [],
            "recommendations": []
        }
    
    def run_git(self, cmd):
        """Execute git command"""
        try:
            result = subprocess.run(
                ["git"] + cmd,
                capture_output=True,
                text=True,
                cwd="."
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:
            print(f"Git error: {e}")
            return None
    
    def get_current_branch(self):
        """Get current branch name"""
        return self.run_git(["branch", "--show-current"]) or "unknown"
    
    def analyze_current_state(self):
        """Analyze current branch state"""
        print("🔍 Analyzing current state...")
        
        # Get current files
        current_files = set()
        for py_file in Path(".").rglob("*.py"):
            if "venv" not in str(py_file) and "node_modules" not in str(py_file):
                current_files.add(str(py_file.relative_to(".")))
        
        for ts_file in Path(".").rglob("*.ts*"):
            if "node_modules" not in str(ts_file):
                current_files.add(str(ts_file.relative_to(".")))
        
        self.analysis["current_state"] = {
            "files": sorted(list(current_files)),
            "file_count": len(current_files)
        }
        
        print(f"  ✅ Current state: {len(current_files)} files")
    
    def get_all_branches(self):
        """Get all branch names"""
        branches = []
        
        # Local branches
        local = self.run_git(["branch", "--format=%(refname:short)"])
        if local:
            branches.extend([b.strip() for b in local.split("\n") if b.strip()])
        
        # Remote branches
        remote = self.run_git(["branch", "-r", "--format=%(refname:short)"])
        if remote:
            for b in remote.split("\n"):
                b = b.strip()
                if b and "HEAD" not in b:
                    branches.append(b)
        
        return branches
    
    def analyze_branch(self, branch):
        """Analyze a specific branch"""
        print(f"  📊 Analyzing {branch}...")
        
        # Get commit message
        commit_msg = self.run_git(["log", branch, "-1", "--format=%s"])
        
        # Get files in branch
        files_output = self.run_git(["ls-tree", "-r", "--name-only", branch])
        branch_files = set()
        if files_output:
            branch_files = set([f.strip() for f in files_output.split("\n") if f.strip()])
        
        # Get diff summary against current
        diff_output = self.run_git(["diff", "--name-status", f"{self.current_branch}...{branch}"])
        changes = []
        if diff_output:
            for line in diff_output.split("\n"):
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        changes.append({
                            "status": parts[0],
                            "file": parts[1]
                        })
        
        return {
            "branch": branch,
            "commit_message": commit_msg or "",
            "file_count": len(branch_files),
            "changes": changes,
            "unique_files": list(branch_files - set(self.analysis["current_state"]["files"]))
        }
    
    def identify_missing_features(self):
        """Identify features missing from current branch"""
        print("\n🔍 Identifying missing features...")
        
        current_files = set(self.analysis["current_state"]["files"])
        
        for branch, info in self.analysis["branch_features"].items():
            if branch == self.current_branch:
                continue
            
            unique_files = info.get("unique_files", [])
            
            # Categorize missing files
            missing_py = [f for f in unique_files if f.endswith(".py")]
            missing_ts = [f for f in unique_files if f.endswith((".ts", ".tsx"))]
            missing_tools = [f for f in unique_files if "tools/" in f or "aurora_" in f]
            
            if missing_py or missing_ts or missing_tools:
                feature = {
                    "branch": branch,
                    "commit": info.get("commit_message", ""),
                    "missing_python": missing_py,
                    "missing_typescript": missing_ts,
                    "missing_tools": missing_tools,
                    "total_missing": len(unique_files)
                }
                
                self.analysis["missing_features"].append(feature)
        
        print(f"  ✅ Found {len(self.analysis['missing_features'])} branches with unique features")
    
    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print("\n💡 Generating recommendations...")
        
        # Group by importance
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for feature in self.analysis["missing_features"]:
            branch = feature["branch"]
            
            # High priority: Aurora tools or core functionality
            if any("aurora_" in f for f in feature["missing_tools"]):
                priority = "HIGH"
                high_priority.append(feature)
            # Medium priority: TypeScript/React features
            elif feature["missing_typescript"]:
                priority = "MEDIUM"
                medium_priority.append(feature)
            # Low priority: Other files
            else:
                priority = "LOW"
                low_priority.append(feature)
        
        # Generate recommendations
        if high_priority:
            self.analysis["recommendations"].append({
                "priority": "HIGH",
                "category": "Core Aurora Tools",
                "action": f"Review {len(high_priority)} branches with Aurora tools/capabilities",
                "branches": [f["branch"] for f in high_priority]
            })
        
        if medium_priority:
            self.analysis["recommendations"].append({
                "priority": "MEDIUM",
                "category": "Frontend Features",
                "action": f"Review {len(medium_priority)} branches with UI/UX enhancements",
                "branches": [f["branch"] for f in medium_priority]
            })
        
        if low_priority:
            self.analysis["recommendations"].append({
                "priority": "LOW",
                "category": "Misc Files",
                "action": f"Review {len(low_priority)} branches with other changes",
                "branches": [f["branch"] for f in low_priority]
            })
        
        print(f"  ✅ Generated {len(self.analysis['recommendations'])} recommendations")
    
    def save_results(self):
        """Save analysis results"""
        json_file = Path("AURORA_BRANCH_COMPARISON_ANALYSIS.json")
        with open(json_file, "w") as f:
            json.dump(self.analysis, f, indent=2)
        
        # Generate markdown report
        md_file = Path("AURORA_BRANCH_COMPARISON_REPORT.md")
        with open(md_file, "w") as f:
            f.write("# 🌟 Aurora Branch Comparison Report\n\n")
            f.write(f"**Generated:** {self.analysis['timestamp']}\n")
            f.write(f"**Current Branch:** `{self.current_branch}`\n\n")
            f.write("---\n\n")
            
            # Current State
            f.write("## 📊 Current State\n\n")
            f.write(f"- **Total Files:** {self.analysis['current_state']['file_count']}\n\n")
            
            # Missing Features
            f.write("## 🔍 Missing Features Analysis\n\n")
            if self.analysis["missing_features"]:
                for feature in sorted(self.analysis["missing_features"], 
                                     key=lambda x: x["total_missing"], reverse=True)[:10]:
                    f.write(f"### {feature['branch']}\n\n")
                    f.write(f"**Commit:** {feature['commit']}\n\n")
                    f.write(f"**Missing Files:** {feature['total_missing']}\n\n")
                    
                    if feature["missing_tools"]:
                        f.write("**Aurora Tools:**\n")
                        for tool in feature["missing_tools"][:5]:
                            f.write(f"- `{tool}`\n")
                        if len(feature["missing_tools"]) > 5:
                            f.write(f"- ... and {len(feature['missing_tools']) - 5} more\n")
                        f.write("\n")
                    
                    if feature["missing_python"]:
                        f.write(f"**Python Files:** {len(feature['missing_python'])}\n\n")
                    
                    if feature["missing_typescript"]:
                        f.write(f"**TypeScript Files:** {len(feature['missing_typescript'])}\n\n")
                    
                    f.write("---\n\n")
            else:
                f.write("✅ No missing features found - current branch is up to date!\n\n")
            
            # Recommendations
            f.write("## 💡 Recommendations\n\n")
            for rec in self.analysis["recommendations"]:
                f.write(f"### {rec['priority']} Priority: {rec['category']}\n\n")
                f.write(f"**Action:** {rec['action']}\n\n")
                f.write("**Branches to Review:**\n")
                for branch in rec["branches"][:5]:
                    f.write(f"- `{branch}`\n")
                if len(rec["branches"]) > 5:
                    f.write(f"- ... and {len(rec['branches']) - 5} more\n")
                f.write("\n---\n\n")
        
        print(f"\n💾 Results saved:")
        print(f"  - {json_file}")
        print(f"  - {md_file}")
    
    def run(self):
        """Run complete analysis"""
        print("=" * 70)
        print("🌌 AURORA BRANCH COMPARISON ANALYZER")
        print("=" * 70)
        
        # Analyze current state
        self.analyze_current_state()
        
        # Get and analyze all branches
        print("\n📋 Analyzing branches...")
        branches = self.get_all_branches()
        print(f"  Found {len(branches)} branches")
        
        for branch in branches:
            info = self.analyze_branch(branch)
            self.analysis["branch_features"][branch] = info
        
        # Identify missing features
        self.identify_missing_features()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Save results
        self.save_results()
        
        print("\n" + "=" * 70)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 70)
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"  - Branches analyzed: {len(branches)}")
        print(f"  - Branches with unique features: {len(self.analysis['missing_features'])}")
        print(f"  - Recommendations: {len(self.analysis['recommendations'])}")
        
        if self.analysis["recommendations"]:
            print(f"\n🎯 Priority Actions:")
            for rec in self.analysis["recommendations"]:
                print(f"  - [{rec['priority']}] {rec['action']}")


if __name__ == "__main__":
    comparator = AuroraBranchComparator()
    comparator.run()
