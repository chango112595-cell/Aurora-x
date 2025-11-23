"""
Complete Repository Forensic Analysis
Processes all Git history data and generates comprehensive report
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class RepositoryForensics:
    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.forensics = {
            "analysis_timestamp": datetime.now().isoformat(),
            "repository": "Aurora-x",
            "summary": {},
            "complete_history": {},
            "branches": {},
            "aurora_files": {},
            "current_state": {},
            "statistics": {}
        }

    def parse_complete_history(self):
        """Parse complete commit history"""
        print("🔍 Parsing complete Git history (33,082 lines)...")

        history_file = self.repo_root / "repo_complete_history.txt"
        commits = {}
        current_commit = None

        with open(history_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if '|' in line and not line[0].isdigit():
                    # Commit line
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commit_hash = parts[0]
                        current_commit = {
                            "hash": commit_hash[:8],
                            "date": parts[1],
                            "author": parts[2],
                            "message": parts[3],
                            "files_changed": []
                        }
                        commits[commit_hash[:8]] = current_commit
                else:
                    # File change line
                    if current_commit and '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            current_commit['files_changed'].append({
                                "added": parts[0] if parts[0].isdigit() else 0,
                                "deleted": parts[1] if parts[1].isdigit() else 0,
                                "file": parts[2]
                            })

        print(f"   ✅ Parsed {len(commits)} unique commits")
        self.forensics['complete_history'] = {
            "total_commits": len(commits),
            "commits": commits
        }

        return commits

    def parse_branches(self):
        """Parse all branches"""
        print("🌿 Parsing all branches (34 branches)...")

        branches_file = self.repo_root / "repo_all_branches.txt"
        branches = {}

        with open(branches_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        branch_name = parts[0]
                        branches[branch_name] = {
                            "name": branch_name,
                            "last_commit_date": parts[1] if len(parts) > 1 else "",
                            "last_author": parts[2] if len(parts) > 2 else "",
                            "last_message": parts[3] if len(parts) > 3 else ""
                        }

        print(f"   ✅ Parsed {len(branches)} branches")
        self.forensics['branches'] = {
            "total_branches": len(branches),
            "branch_list": branches
        }

        return branches

    def parse_aurora_history(self):
        """Parse Aurora file history"""
        print("⚡ Parsing Aurora file history (13,943 lines)...")

        aurora_file = self.repo_root / "repo_aurora_file_history.txt"
        aurora_commits = []
        aurora_files_tracked = set()
        current_commit = None

        with open(aurora_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if '|' in line and not line[0] in ['A', 'M', 'D', 'R']:
                    # Commit line
                    parts = line.split('|')
                    if len(parts) >= 4:
                        current_commit = {
                            "hash": parts[0][:8],
                            "date": parts[1],
                            "author": parts[2],
                            "message": parts[3],
                            "files": []
                        }
                        aurora_commits.append(current_commit)
                elif current_commit:
                    # File status line (A/M/D/R followed by filename)
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        status = parts[0]
                        filename = parts[1]
                        aurora_files_tracked.add(filename)
                        current_commit['files'].append({
                            "status": status,
                            "file": filename
                        })

        print(
            f"   ✅ Tracked {len(aurora_files_tracked)} Aurora files across {len(aurora_commits)} commits")

        self.forensics['aurora_files'] = {
            "total_aurora_commits": len(aurora_commits),
            "unique_aurora_files": len(aurora_files_tracked),
            "aurora_files_list": sorted(list(aurora_files_tracked)),
            "aurora_commit_history": aurora_commits[:100]  # Top 100 for report
        }

        return aurora_files_tracked

    def parse_all_files_ever(self):
        """Parse all files that ever existed"""
        print("📁 Parsing all files ever created (5,812 files)...")

        files_file = self.repo_root / "repo_all_files_ever.txt"
        all_files = []

        with open(files_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line:
                    all_files.append(line)

        # Categorize files
        by_extension = defaultdict(int)
        aurora_files = []

        for file_path in all_files:
            ext = Path(file_path).suffix
            by_extension[ext] += 1

            if 'aurora' in file_path.lower():
                aurora_files.append(file_path)

        print(f"   ✅ Catalogued {len(all_files)} files")
        print(f"   ✅ Found {len(aurora_files)} Aurora-related files")

        self.forensics['statistics']['all_files_ever'] = {
            "total": len(all_files),
            "by_extension": dict(by_extension),
            "aurora_files_count": len(aurora_files)
        }

        return all_files

    def parse_current_state(self):
        """Parse current working tree state"""
        print("📊 Analyzing current state...")

        # Read status
        status_file = self.repo_root / "repo_current_changes.txt"
        staged_file = self.repo_root / "repo_staged.txt"
        unstaged_file = self.repo_root / "repo_unstaged.txt"

        current_changes = []
        if status_file.exists():
            with open(status_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        current_changes.append(line)

        staged = []
        if staged_file.exists():
            with open(staged_file, 'r', encoding='utf-8', errors='ignore') as f:
                staged = [l.strip() for l in f if l.strip()]

        unstaged = []
        if unstaged_file.exists():
            with open(unstaged_file, 'r', encoding='utf-8', errors='ignore') as f:
                unstaged = [l.strip() for l in f if l.strip()]

        print(f"   ✅ Current changes: {len(current_changes)} files")
        print(f"   ✅ Staged: {len(staged)} files")
        print(f"   ✅ Unstaged: {len(unstaged)} files")

        self.forensics['current_state'] = {
            "modified_files": current_changes,
            "staged_count": len(staged),
            "unstaged_count": len(unstaged),
            "working_tree_clean": len(current_changes) == 0
        }

        return current_changes

    def parse_reflog(self):
        """Parse reflog for complete operation history"""
        print("📜 Parsing reflog (623 operations)...")

        reflog_file = self.repo_root / "repo_reflog.txt"
        operations = []

        with open(reflog_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        operations.append({
                            "hash": parts[0][:8],
                            "ref": parts[1],
                            "operation": parts[2],
                            "message": parts[3] if len(parts) > 3 else ""
                        })

        print(f"   ✅ Parsed {len(operations)} operations")

        self.forensics['statistics']['reflog'] = {
            "total_operations": len(operations),
            "recent_operations": operations[:50]  # Last 50
        }

        return operations

    def generate_statistics(self):
        """Generate comprehensive statistics"""
        print("\n📊 Generating statistics...")

        commits = self.forensics['complete_history']
        branches = self.forensics['branches']
        aurora = self.forensics['aurora_files']

        self.forensics['summary'] = {
            "total_commits_all_branches": commits['total_commits'],
            "total_branches": branches['total_branches'],
            "aurora_specific_commits": aurora['total_aurora_commits'],
            "unique_aurora_files_tracked": aurora['unique_aurora_files'],
            "current_working_tree_status": "Clean" if self.forensics['current_state']['working_tree_clean'] else "Modified",
            "repository_age": "From beginning to 2025-11-23"
        }

        print(f"\n✅ Statistics generated")

    def save_forensic_report(self):
        """Save complete forensic analysis"""
        print("\n💾 Saving forensic reports...")

        # Save JSON
        json_file = self.repo_root / "COMPLETE_REPOSITORY_FORENSICS.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.forensics, f, indent=2)

        print(f"   ✅ JSON report: {json_file}")

        # Save Markdown
        md_file = self.repo_root / "COMPLETE_REPOSITORY_FORENSICS.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# 🔍 Complete Repository Forensic Analysis\n\n")
            f.write(
                f"**Generated:** {self.forensics['analysis_timestamp']}\n\n")

            f.write("## 📊 Executive Summary\n\n")
            for key, value in self.forensics['summary'].items():
                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")

            f.write("\n## 🌿 All Branches\n\n")
            f.write(
                f"Total: {self.forensics['branches']['total_branches']} branches\n\n")
            for branch_name, branch_data in list(self.forensics['branches']['branch_list'].items())[:20]:
                f.write(f"### {branch_name}\n")
                f.write(
                    f"- Last commit: {branch_data.get('last_commit_date', 'N/A')}\n")
                f.write(
                    f"- Author: {branch_data.get('last_author', 'N/A')}\n\n")

            f.write("\n## ⚡ Aurora Files Tracked\n\n")
            f.write(
                f"Total: {self.forensics['aurora_files']['unique_aurora_files']} unique Aurora files\n\n")
            for aurora_file in self.forensics['aurora_files']['aurora_files_list'][:50]:
                f.write(f"- `{aurora_file}`\n")

            f.write("\n## 📈 Repository Statistics\n\n")
            if 'all_files_ever' in self.forensics['statistics']:
                stats = self.forensics['statistics']['all_files_ever']
                f.write(f"- **Total files ever created:** {stats['total']}\n")
                f.write(
                    f"- **Aurora-related files:** {stats['aurora_files_count']}\n\n")

                f.write("### Files by Extension\n\n")
                for ext, count in sorted(stats['by_extension'].items(), key=lambda x: x[1], reverse=True)[:20]:
                    f.write(
                        f"- `{ext if ext else '(no extension)'}`: {count} files\n")

            f.write("\n## 📊 Current State\n\n")
            current = self.forensics['current_state']
            f.write(
                f"- **Working tree:** {'✅ Clean' if current['working_tree_clean'] else '⚠️ Modified'}\n")
            f.write(f"- **Staged changes:** {current['staged_count']}\n")
            f.write(f"- **Unstaged changes:** {current['unstaged_count']}\n")

        print(f"   ✅ Markdown report: {md_file}")
        print("\n" + "="*80)

    def run(self):
        """Run complete forensic analysis"""
        print("="*80)
        print("🔍 COMPLETE REPOSITORY FORENSIC ANALYSIS")
        print("="*80)
        print()

        # Parse all data
        self.parse_complete_history()
        self.parse_branches()
        self.parse_aurora_history()
        self.parse_all_files_ever()
        self.parse_current_state()
        self.parse_reflog()

        # Generate statistics
        self.generate_statistics()

        # Save reports
        self.save_forensic_report()

        print("\n✅ FORENSIC ANALYSIS COMPLETE")
        print("="*80)
        print("\n📁 Reports generated:")
        print("   - COMPLETE_REPOSITORY_FORENSICS.json (detailed data)")
        print("   - COMPLETE_REPOSITORY_FORENSICS.md (human-readable)")
        print("\n🎯 Ready for next step.\n")


if __name__ == "__main__":
    forensics = RepositoryForensics()
    forensics.run()
