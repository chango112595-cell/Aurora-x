
#!/usr/bin/env python3
"""
Aurora Comprehensive Repository Analysis
Analyzes all branches, commits, files, and current state to identify improvements needed
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class AuroraComprehensiveAnalyzer:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "git_analysis": {},
            "file_analysis": {},
            "system_state": {},
            "recommendations": [],
            "improvement_priorities": []
        }
        
    def run_git_command(self, cmd):
        """Execute git command and return output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd="."
            )
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"
    
    def analyze_all_branches(self):
        """Analyze all local and remote branches"""
        print("🔍 Analyzing all branches...")
        
        # Get all branches
        local_branches = self.run_git_command("git branch --format='%(refname:short)'").split('\n')
        remote_branches = self.run_git_command("git branch -r --format='%(refname:short)'").split('\n')
        
        branch_data = {}
        
        for branch in local_branches + remote_branches:
            branch = branch.strip()
            if not branch or branch.startswith('origin/HEAD'):
                continue
                
            try:
                # Get commit count
                commit_count = self.run_git_command(f"git rev-list --count {branch}")
                
                # Get last commit info
                last_commit = self.run_git_command(
                    f"git log {branch} -1 --format='%H|%an|%ae|%ad|%s'"
                )
                
                if last_commit and '|' in last_commit:
                    parts = last_commit.split('|')
                    branch_data[branch] = {
                        "commit_count": commit_count,
                        "last_commit_hash": parts[0],
                        "last_author": parts[1],
                        "last_email": parts[2],
                        "last_date": parts[3],
                        "last_message": parts[4] if len(parts) > 4 else ""
                    }
            except Exception as e:
                print(f"⚠️  Could not analyze {branch}: {e}")
        
        self.results["git_analysis"]["branches"] = branch_data
        self.results["git_analysis"]["total_branches"] = len(branch_data)
        
        print(f"✅ Analyzed {len(branch_data)} branches")
    
    def analyze_current_branch_state(self):
        """Analyze staged, unstaged, and untracked files on current branch"""
        print("🔍 Analyzing current branch state...")
        
        current_branch = self.run_git_command("git branch --show-current")
        
        # Get staged files
        staged = self.run_git_command("git diff --cached --name-status")
        
        # Get unstaged files
        unstaged = self.run_git_command("git diff --name-status")
        
        # Get untracked files
        untracked = self.run_git_command("git ls-files --others --exclude-standard")
        
        self.results["git_analysis"]["current_branch"] = {
            "name": current_branch,
            "staged_files": staged.split('\n') if staged else [],
            "unstaged_files": unstaged.split('\n') if unstaged else [],
            "untracked_files": untracked.split('\n') if untracked else []
        }
        
        print(f"✅ Current branch: {current_branch}")
    
    def analyze_commit_history(self):
        """Analyze commit history across all branches"""
        print("🔍 Analyzing commit history...")
        
        # Get all commits
        all_commits = self.run_git_command(
            "git log --all --format='%H|%an|%ad|%s' --date=iso"
        )
        
        commits = []
        for line in all_commits.split('\n'):
            if '|' in line:
                parts = line.split('|')
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3] if len(parts) > 3 else ""
                })
        
        self.results["git_analysis"]["total_commits"] = len(commits)
        self.results["git_analysis"]["recent_commits"] = commits[:50]  # Last 50
        
        print(f"✅ Analyzed {len(commits)} commits")
    
    def analyze_file_structure(self):
        """Analyze repository file structure"""
        print("🔍 Analyzing file structure...")
        
        file_stats = {
            "python_files": 0,
            "typescript_files": 0,
            "javascript_files": 0,
            "markdown_files": 0,
            "json_files": 0,
            "total_files": 0,
            "large_files": []
        }
        
        for root, dirs, files in os.walk("."):
            # Skip hidden directories and common excludes
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
            
            for file in files:
                file_stats["total_files"] += 1
                file_path = os.path.join(root, file)
                
                # Count by extension
                if file.endswith('.py'):
                    file_stats["python_files"] += 1
                elif file.endswith('.ts') or file.endswith('.tsx'):
                    file_stats["typescript_files"] += 1
                elif file.endswith('.js') or file.endswith('.jsx'):
                    file_stats["javascript_files"] += 1
                elif file.endswith('.md'):
                    file_stats["markdown_files"] += 1
                elif file.endswith('.json'):
                    file_stats["json_files"] += 1
                
                # Check file size
                try:
                    size = os.path.getsize(file_path)
                    if size > 1_000_000:  # Files > 1MB
                        file_stats["large_files"].append({
                            "path": file_path,
                            "size_mb": round(size / 1_000_000, 2)
                        })
                except:
                    pass
        
        self.results["file_analysis"] = file_stats
        print(f"✅ Analyzed {file_stats['total_files']} files")
    
    def analyze_system_state(self):
        """Analyze Aurora's current system state"""
        print("🔍 Analyzing Aurora's system state...")
        
        # Check if key files exist
        key_files = {
            "aurora_core.py": Path("aurora_core.py").exists(),
            "aurora_x/main.py": Path("aurora_x/main.py").exists(),
            "server/index.ts": Path("server/index.ts").exists(),
            "client/src/main.tsx": Path("client/src/main.tsx").exists(),
            "package.json": Path("package.json").exists(),
            "requirements.txt": Path("requirements.txt").exists()
        }
        
        # Check for analysis reports
        analysis_files = list(Path(".").glob("AURORA_*_ANALYSIS*.md"))
        
        self.results["system_state"] = {
            "key_files_present": key_files,
            "analysis_reports_count": len(analysis_files),
            "analysis_reports": [str(f) for f in analysis_files[:10]]
        }
        
        print(f"✅ System state analyzed")
    
    def generate_recommendations(self):
        """Generate improvement recommendations based on analysis"""
        print("🔍 Generating recommendations...")
        
        recommendations = []
        priorities = []
        
        # Check merge conflicts
        if self.results["git_analysis"].get("current_branch"):
            staged = self.results["git_analysis"]["current_branch"].get("staged_files", [])
            unstaged = self.results["git_analysis"]["current_branch"].get("unstaged_files", [])
            
            if any("conflict" in str(f).lower() for f in staged + unstaged):
                recommendations.append({
                    "priority": "HIGH",
                    "category": "Git Conflicts",
                    "issue": "Merge conflicts detected",
                    "action": "Resolve all merge conflicts in affected files"
                })
                priorities.append("Resolve merge conflicts")
        
        # Check for large files
        large_files = self.results["file_analysis"].get("large_files", [])
        if len(large_files) > 5:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "File Management",
                "issue": f"{len(large_files)} files over 1MB detected",
                "action": "Consider archiving or optimizing large files"
            })
        
        # Check branch count
        branch_count = self.results["git_analysis"].get("total_branches", 0)
        if branch_count > 20:
            recommendations.append({
                "priority": "LOW",
                "category": "Branch Cleanup",
                "issue": f"{branch_count} branches exist",
                "action": "Consider cleaning up old/merged branches"
            })
        
        # Check for missing key files
        missing_files = [k for k, v in self.results["system_state"]["key_files_present"].items() if not v]
        if missing_files:
            recommendations.append({
                "priority": "HIGH",
                "category": "System Integrity",
                "issue": f"Missing key files: {', '.join(missing_files)}",
                "action": "Restore or recreate missing system files"
            })
            priorities.append("Restore missing system files")
        
        self.results["recommendations"] = recommendations
        self.results["improvement_priorities"] = priorities
        
        print(f"✅ Generated {len(recommendations)} recommendations")
    
    def save_results(self):
        """Save analysis results to file"""
        output_file = "AURORA_COMPREHENSIVE_ANALYSIS_RESULTS.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Analysis saved to: {output_file}")
        
        # Also create a summary markdown
        self.create_summary_markdown()
    
    def create_summary_markdown(self):
        """Create human-readable summary"""
        summary_file = "AURORA_ANALYSIS_SUMMARY.md"
        
        with open(summary_file, 'w') as f:
            f.write("# 🌌 Aurora Comprehensive Analysis Summary\n\n")
            f.write(f"**Generated:** {self.results['timestamp']}\n\n")
            
            f.write("## 📊 Repository Overview\n\n")
            f.write(f"- **Total Branches:** {self.results['git_analysis'].get('total_branches', 0)}\n")
            f.write(f"- **Total Commits:** {self.results['git_analysis'].get('total_commits', 0)}\n")
            f.write(f"- **Total Files:** {self.results['file_analysis'].get('total_files', 0)}\n")
            f.write(f"- **Python Files:** {self.results['file_analysis'].get('python_files', 0)}\n")
            f.write(f"- **TypeScript Files:** {self.results['file_analysis'].get('typescript_files', 0)}\n\n")
            
            f.write("## 🎯 Top Priorities\n\n")
            for priority in self.results.get('improvement_priorities', []):
                f.write(f"- {priority}\n")
            f.write("\n")
            
            f.write("## 💡 Recommendations\n\n")
            for rec in self.results.get('recommendations', []):
                f.write(f"### {rec['priority']}: {rec['category']}\n")
                f.write(f"- **Issue:** {rec['issue']}\n")
                f.write(f"- **Action:** {rec['action']}\n\n")
        
        print(f"✅ Summary saved to: {summary_file}")
    
    def run_full_analysis(self):
        """Run complete analysis"""
        print("\n" + "="*80)
        print("🌌 AURORA COMPREHENSIVE REPOSITORY ANALYSIS")
        print("="*80 + "\n")
        
        self.analyze_all_branches()
        self.analyze_current_branch_state()
        self.analyze_commit_history()
        self.analyze_file_structure()
        self.analyze_system_state()
        self.generate_recommendations()
        self.save_results()
        
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE")
        print("="*80 + "\n")
        
        # Print summary
        print("📊 Quick Summary:")
        print(f"   - Analyzed {self.results['git_analysis'].get('total_branches', 0)} branches")
        print(f"   - Found {self.results['git_analysis'].get('total_commits', 0)} commits")
        print(f"   - Scanned {self.results['file_analysis'].get('total_files', 0)} files")
        print(f"   - Generated {len(self.results['recommendations'])} recommendations")
        print("\nSee AURORA_ANALYSIS_SUMMARY.md for details\n")


if __name__ == "__main__":
    analyzer = AuroraComprehensiveAnalyzer()
    analyzer.run_full_analysis()
