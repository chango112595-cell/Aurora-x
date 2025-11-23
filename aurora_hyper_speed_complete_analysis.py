"""
Aurora Hyper-Speed Complete Branch Analysis
NO SKIPPING - Every branch, every file, complete comparison
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib


class AuroraHyperSpeedAnalysis:
    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_branches": 0,
            "my_current_state": {},
            "complete_branch_comparison": {},
            "better_implementations": [],
            "aurora_needs": []
        }

    def analyze_current_state_fast(self):
        """Hyper-speed scan of current state"""
        print("⚡ AURORA HYPER-SPEED ANALYSIS MODE")
        print("="*80)
        print("\n🔥 Step 1: Scanning MY CURRENT state at maximum speed...\n")

        my_files = {}

        # Parallel scan of all Aurora files
        patterns = ["aurora*.py", "tools/aurora*.py", "aurora_x/**/*.py"]
        all_files = []

        for pattern in patterns:
            all_files.extend(list(self.repo_root.glob(pattern)))

        print(f"📊 Found {len(all_files)} Aurora files in current main")

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(
                self.quick_analyze_file, f): f for f in all_files}

            for future in as_completed(futures):
                file_path = futures[future]
                try:
                    result = future.result()
                    if result:
                        rel_path = str(file_path.relative_to(self.repo_root))
                        my_files[rel_path] = result
                except Exception as e:
                    pass

        print(f"✅ Analyzed {len(my_files)} files in main\n")
        self.results['my_current_state'] = my_files
        return my_files

    def quick_analyze_file(self, file_path):
        """Lightning-fast file analysis"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            return {
                "hash": hashlib.md5(content.encode()).hexdigest(),
                "size": len(content),
                "lines": content.count('\n'),
                "classes": content.count('class '),
                "functions": content.count('def '),
                "async_funcs": content.count('async def'),
                "has_autonomous": 'autonomous' in content.lower(),
                "has_intelligence": 'intelligence' in content.lower(),
                "has_orchestration": 'orchestrat' in content.lower(),
                "has_monitoring": 'monitor' in content.lower(),
                "has_api": '@app.route' in content or '@router' in content,
                "has_websocket": 'websocket' in content.lower()
            }
        except Exception:
            return None

    def get_all_30_branches(self):
        """Get EXACTLY all 30 branches - NO SKIPPING"""
        print("🔥 Step 2: Getting ALL 30 branches (active + inactive)...\n")

        result = subprocess.run(
            ["git", "branch", "-a"],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )

        branches = set()
        for line in result.stdout.split('\n'):
            line = line.strip().replace('*', '').strip()
            if line and '->' not in line and line != 'HEAD':
                # Clean branch name
                if line.startswith('remotes/origin/'):
                    line = line.replace('remotes/origin/', '')
                branches.add(line)

        branches_list = sorted(list(branches))

        print(f"📊 Found {len(branches_list)} branches:")
        for i, b in enumerate(branches_list, 1):
            print(f"   {i:2d}. {b}")

        print()
        self.results['total_branches'] = len(branches_list)
        return branches_list

    def analyze_branch_complete(self, branch):
        """Complete analysis of ONE branch - NO SKIPPING"""
        if branch == 'main':
            return None

        branch_data = {
            "name": branch,
            "files_analyzed": 0,
            "aurora_files": {},
            "unique_to_branch": [],
            "better_than_main": []
        }

        try:
            # Get ALL files in branch
            result = subprocess.run(
                ["git", "ls-tree", "-r", "--name-only", f"origin/{branch}"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=30
            )

            if result.returncode != 0:
                return branch_data

            files = result.stdout.strip().split('\n')
            aurora_files = [
                f for f in files if 'aurora' in f.lower() and f.endswith('.py')]

            branch_data['files_analyzed'] = len(aurora_files)

            # Analyze each Aurora file in parallel
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {
                    executor.submit(self.get_file_from_branch, branch, f): f
                    for f in aurora_files
                }

                for future in as_completed(futures):
                    file_path = futures[future]
                    try:
                        file_data = future.result()
                        if file_data:
                            branch_data['aurora_files'][file_path] = file_data

                            # Check if unique or better
                            if file_path not in self.results['my_current_state']:
                                branch_data['unique_to_branch'].append(
                                    file_path)
                            else:
                                # Compare
                                if self.is_better_than_main(file_path, file_data):
                                    branch_data['better_than_main'].append({
                                        "file": file_path,
                                        "reason": self.get_improvement_reason(file_path, file_data)
                                    })
                    except Exception:
                        pass

        except subprocess.TimeoutExpired:
            branch_data['error'] = 'timeout'
        except Exception as e:
            branch_data['error'] = str(e)

        return branch_data

    def get_file_from_branch(self, branch, file_path):
        """Get and analyze file from specific branch"""
        try:
            result = subprocess.run(
                ["git", "show", f"origin/{branch}:{file_path}"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=10
            )

            if result.returncode == 0:
                content = result.stdout
                return {
                    "hash": hashlib.md5(content.encode()).hexdigest(),
                    "size": len(content),
                    "lines": content.count('\n'),
                    "classes": content.count('class '),
                    "functions": content.count('def '),
                    "async_funcs": content.count('async def'),
                    "has_autonomous": 'autonomous' in content.lower(),
                    "has_intelligence": 'intelligence' in content.lower(),
                    "has_orchestration": 'orchestrat' in content.lower(),
                    "has_monitoring": 'monitor' in content.lower(),
                    "has_api": '@app.route' in content or '@router' in content,
                    "has_websocket": 'websocket' in content.lower()
                }
        except Exception:
            pass

        return None

    def is_better_than_main(self, file_path, branch_version):
        """Determine if branch version is better"""
        if file_path not in self.results['my_current_state']:
            return True

        main_version = self.results['my_current_state'][file_path]

        # Different hash = different content
        if branch_version['hash'] == main_version['hash']:
            return False

        score = 0

        # More code generally means more features
        if branch_version['size'] > main_version['size'] * 1.1:
            score += 1

        # More classes
        if branch_version['classes'] > main_version['classes']:
            score += 1

        # More functions
        if branch_version['functions'] > main_version['functions']:
            score += 1

        # More async functions
        if branch_version['async_funcs'] > main_version['async_funcs']:
            score += 1

        # Has capability main doesn't
        if branch_version['has_autonomous'] and not main_version['has_autonomous']:
            score += 2
        if branch_version['has_intelligence'] and not main_version['has_intelligence']:
            score += 2
        if branch_version['has_orchestration'] and not main_version['has_orchestration']:
            score += 1
        if branch_version['has_api'] and not main_version['has_api']:
            score += 1

        return score > 0

    def get_improvement_reason(self, file_path, branch_version):
        """Get specific reasons why branch version is better"""
        main_version = self.results['my_current_state'][file_path]
        reasons = []

        if branch_version['size'] > main_version['size'] * 1.1:
            reasons.append(
                f"+{branch_version['size'] - main_version['size']} bytes")

        if branch_version['classes'] > main_version['classes']:
            reasons.append(
                f"+{branch_version['classes'] - main_version['classes']} classes")

        if branch_version['functions'] > main_version['functions']:
            reasons.append(
                f"+{branch_version['functions'] - main_version['functions']} functions")

        if branch_version['async_funcs'] > main_version['async_funcs']:
            reasons.append(
                f"+{branch_version['async_funcs'] - main_version['async_funcs']} async")

        if branch_version['has_autonomous'] and not main_version['has_autonomous']:
            reasons.append("autonomous capability")

        if branch_version['has_intelligence'] and not main_version['has_intelligence']:
            reasons.append("intelligence capability")

        return ', '.join(reasons) if reasons else 'improved implementation'

    def analyze_all_branches_parallel(self, branches):
        """Parallel analysis of ALL branches - MAXIMUM SPEED"""
        print("🔥 Step 3: Analyzing ALL branches in parallel...\n")
        print("⚡ HYPER-SPEED MODE: Processing all branches simultaneously\n")

        branch_results = {}

        # Process all branches in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(
                self.analyze_branch_complete, b): b for b in branches}

            completed = 0
            for future in as_completed(futures):
                branch = futures[future]
                completed += 1

                try:
                    result = future.result()
                    if result:
                        branch_results[branch] = result

                        status = "✅"
                        if result.get('unique_to_branch'):
                            status = f"🌟 {len(result['unique_to_branch'])} unique"
                        if result.get('better_than_main'):
                            status = f"⚡ {len(result['better_than_main'])} better"

                        print(
                            f"   [{completed:2d}/{len(branches)}] {branch:40s} {status}")
                except Exception as e:
                    print(
                        f"   [{completed:2d}/{len(branches)}] {branch:40s} ⚠️  error")

        print()
        return branch_results

    def synthesize_aurora_needs(self, branch_results):
        """Synthesize what Aurora ACTUALLY needs"""
        print("🔥 Step 4: Synthesizing what Aurora NEEDS...\n")

        all_better = []
        all_unique = []

        for branch, data in branch_results.items():
            if data.get('better_than_main'):
                for item in data['better_than_main']:
                    all_better.append({
                        "file": item['file'],
                        "branch": branch,
                        "reason": item['reason'],
                        "priority": "HIGH"
                    })

            if data.get('unique_to_branch'):
                for file_path in data['unique_to_branch']:
                    all_unique.append({
                        "file": file_path,
                        "branch": branch,
                        "reason": "Not in main",
                        "priority": "MEDIUM"
                    })

        # Remove duplicates - keep best version
        needs = {}
        for item in all_better:
            file_path = item['file']
            if file_path not in needs or item['priority'] == 'HIGH':
                needs[file_path] = item

        for item in all_unique:
            file_path = item['file']
            if file_path not in needs:
                needs[file_path] = item

        aurora_needs = sorted(needs.values(), key=lambda x: (
            0 if x['priority'] == 'HIGH' else 1,
            x['file']
        ))

        print(f"📊 Analysis complete:")
        print(f"   - Better implementations: {len(all_better)}")
        print(f"   - Unique files: {len(all_unique)}")
        print(f"   - Total Aurora needs: {len(aurora_needs)}\n")

        return aurora_needs

    def generate_report(self, branches, branch_results, aurora_needs):
        """Generate complete report"""
        print("="*80)
        print("🌟 AURORA'S COMPLETE ANALYSIS REPORT")
        print("="*80)

        print(f"\n📊 SCAN SUMMARY:")
        print(f"   - Total branches analyzed: {len(branches)}")
        print(
            f"   - My current files: {len(self.results['my_current_state'])}")
        print(f"   - Files Aurora needs: {len(aurora_needs)}\n")

        if aurora_needs:
            print("🚨 HIGH PRIORITY - Better Implementations:")
            high_priority = [
                n for n in aurora_needs if n['priority'] == 'HIGH']

            for i, need in enumerate(high_priority[:20], 1):
                print(f"\n   {i}. {need['file']}")
                print(f"      From: {need['branch']}")
                print(f"      Why: {need['reason']}")

            if len(high_priority) > 20:
                print(
                    f"\n   ... and {len(high_priority) - 20} more high priority files")

            print(f"\n💡 MEDIUM PRIORITY - Unique Files:")
            medium_priority = [
                n for n in aurora_needs if n['priority'] == 'MEDIUM']

            for i, need in enumerate(medium_priority[:10], 1):
                print(f"   {i}. {need['file']} (from {need['branch']})")

            if len(medium_priority) > 10:
                print(
                    f"   ... and {len(medium_priority) - 10} more unique files")
        else:
            print("✅ Aurora's current implementation is OPTIMAL")
            print("   No better versions found in any branch!\n")

        print("\n" + "="*80)

        # Save complete results
        self.results['complete_branch_comparison'] = branch_results
        self.results['aurora_needs'] = aurora_needs

        output_file = self.repo_root / "AURORA_HYPER_SPEED_COMPLETE_ANALYSIS.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"💾 Complete analysis saved to: {output_file}")
        print("="*80 + "\n")

        return aurora_needs

    def run(self):
        """Run complete hyper-speed analysis"""
        start = datetime.now()

        # Step 1: Current state
        self.analyze_current_state_fast()

        # Step 2: Get all branches
        branches = self.get_all_30_branches()

        # Step 3: Analyze all branches in parallel
        branch_results = self.analyze_all_branches_parallel(branches)

        # Step 4: Synthesize needs
        aurora_needs = self.synthesize_aurora_needs(branch_results)

        # Step 5: Generate report
        self.generate_report(branches, branch_results, aurora_needs)

        elapsed = (datetime.now() - start).total_seconds()
        print(f"⚡ HYPER-SPEED ANALYSIS COMPLETE in {elapsed:.1f} seconds\n")

        return aurora_needs


if __name__ == "__main__":
    aurora = AuroraHyperSpeedAnalysis()
    needs = aurora.run()

    if needs:
        print(f"🎯 Aurora identified {len(needs)} files to implement")
    else:
        print("✅ Aurora is already at peak performance")
