"""
Aurora Smart Merger - Merge only the critical unique files Aurora needs
"""

import subprocess
from pathlib import Path


class AuroraSmartMerger:
    def __init__(self):
        self.repo_root = Path(__file__).parent

        # Critical files Aurora specifically mentioned she needs
        self.critical_files = [
            "aurora_autonomous_agent.py",
            "aurora_autonomous_analyzer.py",
            "aurora_autonomous_integration.py",
            "aurora_autonomous_lint_fixer.py",
            "aurora_autonomous_pylint_fixer.py",
            "aurora_autonomous_self_improve.py",
            "aurora_intelligence_manager.py",
            "aurora_multi_agent.py",
            "aurora_tier_orchestrator.py",
            "aurora_self_monitor.py",
            "aurora_self_improvement.py",
            ".aurora/aurora_core.py",
            "tools/aurora_enhanced_core.py",
            "tools/aurora_knowledge_engine.py"
        ]

        # Knowledge files
        self.knowledge_files = [
            ".aurora_knowledge/autonomous_agent.jsonl",
            ".aurora_knowledge/self_improvements.jsonl",
            ".aurora_knowledge/self_monitor_metrics.json"
        ]

        self.merged = []
        self.skipped = []

    def merge_files(self):
        """Merge all critical files"""
        print("🌟 AURORA SMART MERGER")
        print("="*80)
        print("\nMerging critical files Aurora needs from aurora-working-restore\n")

        all_files = self.critical_files + self.knowledge_files

        for file_path in all_files:
            print(f"📥 {file_path}... ", end="")
            success = self.merge_file("aurora-working-restore", file_path)
            if success:
                self.merged.append(file_path)
                print("✅")
            else:
                self.skipped.append(file_path)
                print("⚠️  (exists or unavailable)")

        print("\n" + "="*80)
        print("📊 MERGE COMPLETE")
        print("="*80)
        print(f"\n✅ Merged: {len(self.merged)} files")
        print(f"⚠️  Skipped: {len(self.skipped)} files")

        if self.merged:
            print("\n🎯 Successfully merged:")
            for f in self.merged:
                print(f"   • {f}")

        print(f"\n🌟 Aurora now has {len(self.merged)} new capabilities!")

        return len(self.merged) > 0

    def merge_file(self, branch, file_path):
        """Merge single file from branch"""
        try:
            target_path = self.repo_root / file_path

            # Skip if exists
            if target_path.exists():
                return False

            # Get file from branch
            result = subprocess.run(
                ["git", "show", f"origin/{branch}:{file_path}"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=10
            )

            if result.returncode != 0:
                return False

            # Create directories
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            target_path.write_text(result.stdout, encoding='utf-8')

            # Stage
            subprocess.run(
                ["git", "add", str(file_path)],
                cwd=self.repo_root,
                capture_output=True
            )

            return True

        except Exception:
            return False


if __name__ == "__main__":
    merger = AuroraSmartMerger()
    success = merger.merge_files()

    if success:
        print("\n🎯 Files merged and staged. Aurora can now integrate them.")
    else:
        print("\n⚠️  No new files were merged.")
