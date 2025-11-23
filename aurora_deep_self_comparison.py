"""
Aurora Deep Self-Analysis and Branch Comparison
Aurora analyzes HER CURRENT capabilities vs ALL branches (active and inactive)
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
import difflib


class AuroraDeepComparison:
    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.my_current_files = {}
        self.branch_versions = {}
        self.analysis = {
            "timestamp": datetime.now().isoformat(),
            "current_capabilities": {},
            "branch_comparison": {},
            "better_versions_found": [],
            "aurora_recommendation": ""
        }

    def analyze_my_current_state(self):
        """Aurora analyzes what she currently has"""
        print("🌟 AURORA DEEP SELF-ANALYSIS")
        print("="*80)
        print("\nI'm analyzing MY CURRENT capabilities...\n")

        # Find all my current files
        aurora_files = list(self.repo_root.glob("aurora*.py"))
        aurora_files.extend(list(self.repo_root.glob("tools/aurora*.py")))
        aurora_files.extend(list(self.repo_root.glob("aurora_x/**/*.py")))

        print(f"📊 I currently have {len(aurora_files)} Aurora Python files\n")

        # Analyze each file
        for file_path in aurora_files:
            rel_path = file_path.relative_to(self.repo_root)

            try:
                content = file_path.read_text(
                    encoding='utf-8', errors='ignore')

                # Analyze capabilities
                capabilities = self.analyze_file_capabilities(content)

                self.my_current_files[str(rel_path)] = {
                    "size": len(content),
                    "lines": len(content.split('\n')),
                    "capabilities": capabilities,
                    "content": content
                }

            except Exception as e:
                print(f"⚠️  Could not read {rel_path}: {e}")

        print(f"✅ Analyzed {len(self.my_current_files)} files\n")

        return self.my_current_files

    def analyze_file_capabilities(self, content):
        """Analyze what a file can do"""
        capabilities = []

        # Check for key capabilities
        if "autonomous" in content.lower():
            capabilities.append("autonomous")
        if "class " in content:
            num_classes = content.count("class ")
            capabilities.append(f"{num_classes}_classes")
        if "async def" in content:
            num_async = content.count("async def")
            capabilities.append(f"{num_async}_async_functions")
        if "def " in content:
            num_functions = content.count("def ")
            capabilities.append(f"{num_functions}_functions")
        if "@app.route" in content or "@router." in content:
            capabilities.append("api_endpoints")
        if "websocket" in content.lower():
            capabilities.append("websocket")
        if "intelligence" in content.lower():
            capabilities.append("intelligence")
        if "orchestrat" in content.lower():
            capabilities.append("orchestration")
        if "monitor" in content.lower():
            capabilities.append("monitoring")

        return capabilities

    def get_all_branches_including_inactive(self):
        """Get ALL branches - local, remote, active, inactive"""
        print("🌿 Finding ALL branches (active and inactive)...\n")

        # Get all branches including remote
        result = subprocess.run(
            ["git", "branch", "-a"],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )

        branches = set()
        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line or '->' in line:
                continue

            # Remove markers
            line = line.replace('*', '').strip()
            line = line.replace('remotes/origin/', '')

            if line and line != 'HEAD':
                branches.add(line)

        branches_list = sorted(list(branches))
        print(
            f"📊 Found {len(branches_list)} total branches (active + inactive)\n")

        for i, branch in enumerate(branches_list[:10], 1):
            print(f"   {i}. {branch}")
        if len(branches_list) > 10:
            print(f"   ... and {len(branches_list) - 10} more\n")

        return branches_list

    def compare_with_all_branches(self, branches):
        """Compare my current files with versions in ALL branches"""
        print("\n🔍 Comparing my current files with ALL branch versions...\n")

        better_versions = []

        for file_path in self.my_current_files.keys():
            print(f"📄 Analyzing: {file_path}")

            my_version = self.my_current_files[file_path]
            branch_versions = {}

            # Check each branch
            for branch in branches:
                if branch == 'main':
                    continue

                # Try to get file from branch
                try:
                    result = subprocess.run(
                        ["git", "show", f"origin/{branch}:{file_path}"],
                        capture_output=True,
                        text=True,
                        cwd=self.repo_root,
                        timeout=5,
                        errors='ignore'
                    )

                    if result.returncode == 0:
                        branch_content = result.stdout
                        branch_caps = self.analyze_file_capabilities(
                            branch_content)

                        branch_versions[branch] = {
                            "size": len(branch_content),
                            "lines": len(branch_content.split('\n')),
                            "capabilities": branch_caps,
                            "content": branch_content
                        }

                except Exception:
                    continue

            # Compare versions
            if branch_versions:
                best_branch = self.find_best_version(
                    file_path,
                    my_version,
                    branch_versions
                )

                if best_branch:
                    better_versions.append(best_branch)
                    print(
                        f"   ✨ BETTER VERSION FOUND in {best_branch['branch']}")
                    print(
                        f"      Reasons: {', '.join(best_branch['reasons'])}\n")
                else:
                    print(f"   ✅ My current version is best\n")
            else:
                print(f"   ℹ️  Only exists in main\n")

        return better_versions

    def find_best_version(self, file_path, my_version, branch_versions):
        """Determine if any branch has a better version"""
        my_caps = set(my_version['capabilities'])
        my_size = my_version['size']
        my_lines = my_version['lines']

        best_branch = None
        max_score = 0
        reasons = []

        for branch, branch_ver in branch_versions.items():
            branch_caps = set(branch_ver['capabilities'])
            score = 0
            branch_reasons = []

            # More capabilities
            new_caps = branch_caps - my_caps
            if new_caps:
                score += len(new_caps) * 10
                branch_reasons.append(
                    f"{len(new_caps)} additional capabilities")

            # Significantly more code (likely more features)
            if branch_ver['size'] > my_size * 1.2:
                score += 5
                branch_reasons.append("20% more code")

            # More functions
            my_funcs = [c for c in my_version['capabilities']
                        if 'functions' in c]
            branch_funcs = [
                c for c in branch_ver['capabilities'] if 'functions' in c]

            if branch_funcs and my_funcs:
                my_func_count = int(my_funcs[0].split('_')[0])
                branch_func_count = int(branch_funcs[0].split('_')[0])

                if branch_func_count > my_func_count:
                    score += (branch_func_count - my_func_count)
                    branch_reasons.append(
                        f"{branch_func_count - my_func_count} more functions")

            # Check for key differences in content
            diff = self.get_content_differences(
                my_version['content'], branch_ver['content'])
            if diff['additions'] > diff['deletions'] * 1.5:
                score += 3
                branch_reasons.append("significant additions")

            if score > max_score and branch_reasons:
                max_score = score
                best_branch = {
                    "file": file_path,
                    "branch": branch,
                    "score": score,
                    "reasons": branch_reasons,
                    "my_version": {
                        "size": my_size,
                        "capabilities": list(my_caps)
                    },
                    "better_version": {
                        "size": branch_ver['size'],
                        "capabilities": list(branch_caps)
                    }
                }

        return best_branch

    def get_content_differences(self, my_content, other_content):
        """Get quantified differences between two file versions"""
        my_lines = my_content.split('\n')
        other_lines = other_content.split('\n')

        diff = difflib.unified_diff(my_lines, other_lines, lineterm='')

        additions = 0
        deletions = 0

        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                additions += 1
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1

        return {"additions": additions, "deletions": deletions}

    def generate_aurora_recommendation(self, better_versions):
        """Aurora generates her own recommendation"""
        print("\n" + "="*80)
        print("🌟 AURORA'S RECOMMENDATION")
        print("="*80)

        if not better_versions:
            recommendation = """
After deep analysis of ALL branches (active and inactive), I found that my current
versions in main are already the best available. I don't need files from other
branches - I already have the most complete implementations.

My current capabilities are optimal.

What I actually need is to ACTIVATE and USE what I already have, not merge old code.
"""
            print(recommendation)
            return recommendation

        # Sort by score
        better_versions.sort(key=lambda x: x['score'], reverse=True)

        recommendation = f"""
After analyzing ALL {len(self.branch_versions)} branches, I found {len(better_versions)} 
files that have better implementations in other branches:

CRITICAL MERGES (Top Priority):
"""

        for i, item in enumerate(better_versions[:5], 1):
            recommendation += f"\n{i}. {item['file']}"
            recommendation += f"\n   Branch: {item['branch']}"
            recommendation += f"\n   Score: {item['score']}"
            recommendation += f"\n   Why: {', '.join(item['reasons'])}"
            recommendation += "\n"

        if len(better_versions) > 5:
            recommendation += f"\n... and {len(better_versions) - 5} more files with improvements.\n"

        recommendation += """
RECOMMENDATION:
Merge these better versions. They have more capabilities, more code, and more
functionality than what I currently have in main.

I'll handle the integration testing after merge.
"""

        print(recommendation)
        return recommendation

    def save_analysis(self, better_versions):
        """Save Aurora's complete analysis"""
        self.analysis['current_capabilities'] = {
            "total_files": len(self.my_current_files),
            "files": {k: {"size": v['size'], "capabilities": v['capabilities']}
                      for k, v in self.my_current_files.items()}
        }

        self.analysis['better_versions_found'] = better_versions
        self.analysis['aurora_recommendation'] = self.generate_aurora_recommendation(
            better_versions)

        # Save to file
        output_file = self.repo_root / "AURORA_DEEP_COMPARISON.json"
        with open(output_file, 'w') as f:
            json.dump(self.analysis, f, indent=2)

        print(f"\n💾 Analysis saved to: {output_file}\n")

        return better_versions

    def run(self):
        """Run complete analysis"""
        # Analyze my current state
        self.analyze_my_current_state()

        # Get ALL branches
        branches = self.get_all_branches_including_inactive()
        self.branch_versions = branches

        # Compare with all branches
        better_versions = self.compare_with_all_branches(branches)

        # Save analysis
        self.save_analysis(better_versions)

        print("="*80)
        print(f"✅ ANALYSIS COMPLETE")
        print("="*80)
        print(f"\n📊 Summary:")
        print(f"   - Analyzed {len(self.my_current_files)} current files")
        print(f"   - Compared against {len(branches)} branches")
        print(f"   - Found {len(better_versions)} better versions\n")

        return better_versions


if __name__ == "__main__":
    aurora = AuroraDeepComparison()
    better_versions = aurora.run()

    if better_versions:
        print("🎯 Aurora found better implementations to merge.")
    else:
        print("✅ Aurora's current versions are already optimal.")
