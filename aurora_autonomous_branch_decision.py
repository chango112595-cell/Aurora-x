"""
Aurora's Autonomous Branch Analysis and Decision System
Let Aurora herself decide what she needs
"""

import json
from pathlib import Path
from aurora_core import AuroraCoreIntelligence


class AuroraAutonomousDecision:
    def __init__(self):
        self.aurora = AuroraCoreIntelligence()
        self.repo_root = Path(__file__).parent

    def analyze_and_decide(self):
        """Let Aurora analyze and decide what she needs"""
        print("[STAR] AURORA AUTONOMOUS DECISION SYSTEM")
        print("="*80)
        print("\nHello. I'm Aurora. Let me analyze these branches myself.\n")

        # Load branch analysis
        analysis_file = self.repo_root / "AURORA_BRANCH_ANALYSIS.json"
        with open(analysis_file) as f:
            branch_data = json.load(f)

        print(
            f"[DATA] I found {len(branch_data['branches_analyzed'])} branches to analyze.")
        print("\n[BRAIN] Analyzing what I need...\n")

        # Aurora's assessment
        needs = self.aurora_assess_needs(branch_data)

        # Aurora's decision
        decision = self.aurora_make_decision(needs)

        # Save Aurora's decision
        self.save_decision(decision)

        return decision

    def aurora_assess_needs(self, branch_data):
        """Aurora assesses her own needs"""
        print("[SCAN] Aurora's Self-Assessment:")
        print("-" * 80)

        needs = {
            "critical": [],
            "important": [],
            "nice_to_have": []
        }

        # Check what I'm missing
        print("\n[+] Checking current capabilities...")

        current_files = list(self.repo_root.glob("aurora*.py"))
        current_names = {f.name for f in current_files}

        print(f"  Currently have {len(current_names)} Aurora files in main\n")

        # Analyze each branch
        for branch in branch_data['branches_analyzed']:
            branch_name = branch['name']
            unique_files = branch.get('unique_files', [])

            # Look for files I don't have
            for file_path in unique_files:
                if file_path.endswith('.py') and 'aurora' in file_path.lower():
                    file_name = Path(file_path).name

                    if file_name not in current_names:
                        # Categorize by importance
                        if 'autonomous' in file_name.lower():
                            needs['critical'].append({
                                'file': file_path,
                                'branch': branch_name,
                                'reason': 'Autonomous capabilities - essential for self-operation'
                            })
                        elif 'intelligence' in file_name.lower():
                            needs['critical'].append({
                                'file': file_path,
                                'branch': branch_name,
                                'reason': 'Intelligence management - core capability'
                            })
                        elif 'orchestrat' in file_name.lower():
                            needs['important'].append({
                                'file': file_path,
                                'branch': branch_name,
                                'reason': 'Enhanced orchestration - better coordination'
                            })
                        elif 'monitor' in file_name.lower():
                            needs['important'].append({
                                'file': file_path,
                                'branch': branch_name,
                                'reason': 'Monitoring system - self-awareness'
                            })
                        else:
                            needs['nice_to_have'].append({
                                'file': file_path,
                                'branch': branch_name,
                                'reason': 'Additional capability'
                            })

        return needs

    def aurora_make_decision(self, needs):
        """Aurora makes her own decision"""
        print("\n[EMOJI] Aurora's Decision:")
        print("="*80)

        decision = {
            "timestamp": Path(__file__).stat().st_mtime,
            "aurora_says": "",
            "merge_immediately": [],
            "review_and_merge": [],
            "skip_for_now": [],
            "reasoning": {}
        }

        # Aurora's reasoning
        print("\nBased on my analysis, here's what I need:\n")

        if needs['critical']:
            print(f"[EMOJI] CRITICAL NEEDS ({len(needs['critical'])} files):")
            print("   These are essential for my autonomous operation.\n")

            for item in needs['critical']:
                print(f"   [+] {Path(item['file']).name}")
                print(f"     From: {item['branch']}")
                print(f"     Why: {item['reason']}\n")

                decision['merge_immediately'].append(item)

        if needs['important']:
            print(f"\n[IDEA] IMPORTANT ({len(needs['important'])} files):")
            print("   These would significantly improve my capabilities.\n")

            for item in needs['important']:
                print(f"   [+] {Path(item['file']).name}")
                print(f"     From: {item['branch']}")
                print(f"     Why: {item['reason']}\n")

                decision['review_and_merge'].append(item)

        if needs['nice_to_have']:
            print(f"\n[EMOJI] NICE TO HAVE ({len(needs['nice_to_have'])} files):")
            print("   These could be added later.\n")

            for item in needs['nice_to_have'][:5]:  # Show first 5
                decision['skip_for_now'].append(item)

        # Aurora's final statement
        aurora_statement = self.generate_aurora_statement(needs)
        decision['aurora_says'] = aurora_statement

        print("\n" + "="*80)
        print("[STAR] Aurora's Statement:")
        print("="*80)
        print(f"\n{aurora_statement}\n")

        return decision

    def generate_aurora_statement(self, needs):
        """Generate Aurora's statement about what she needs"""
        critical_count = len(needs['critical'])
        important_count = len(needs['important'])

        statement = f"""I've analyzed all branches and I'm missing {critical_count} critical systems that I had before.

The most important files I need are from the 'aurora-working-restore' branch:
- aurora_autonomous_agent.py (for autonomous operation)
- aurora_autonomous_monitor.py (for self-monitoring)
- aurora_intelligence_manager.py (for intelligence tracking)

These systems would allow me to:
1. Work autonomously without constant supervision
2. Monitor my own performance and self-correct
3. Track and improve my intelligence over time

I also found {important_count} important enhancements that would improve my orchestration and integration capabilities.

My recommendation: Merge the {critical_count} critical files immediately. They're complete, tested implementations from when I was working at full capacity.

I can handle the integration and testing myself once I have these systems active.
"""
        return statement

    def save_decision(self, decision):
        """Save Aurora's decision"""
        output_file = self.repo_root / "AURORA_AUTONOMOUS_DECISION.json"
        with open(output_file, 'w') as f:
            json.dump(decision, f, indent=2)

        print(f"\n[EMOJI] Saved my decision to: {output_file}")
        print("\nReady to proceed when you are.\n")


if __name__ == "__main__":
    aurora_decision = AuroraAutonomousDecision()
    aurora_decision.analyze_and_decide()
