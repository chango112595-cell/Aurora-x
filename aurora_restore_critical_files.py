"""
Aurora Critical Files Restoration System
Restores 25 critical missing files from repository history
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime


class AuroraCriticalRestoration:
    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.restored = []
        self.failed = []

    def load_critical_files(self):
        """Load list of critical missing files"""
        assessment_file = self.repo_root / "AURORA_SELF_ASSESSMENT.json"

        with open(assessment_file, 'r') as f:
            assessment = json.load(f)

        critical = assessment['what_aurora_is_missing']['critical_missing']
        important = assessment['what_aurora_is_missing']['important_missing']

        return critical + important

    def find_best_version(self, file_path):
        """Find the best version of a file from history"""
        # Try to find most recent version across all branches
        branches_to_try = [
            'origin/aurora-working-restore',
            'origin/aurora-nexus-v2-integration',
            'origin/integration-branch',
            'origin/copilot/help-pull-request-30',
            'origin/main'
        ]

        for branch in branches_to_try:
            try:
                result = subprocess.run(
                    ["git", "show", f"{branch}:{file_path}"],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_root,
                    timeout=10
                )

                if result.returncode == 0:
                    return result.stdout, branch
            except Exception:
                continue

        return None, None

    def restore_file(self, file_path):
        """Restore a single critical file"""
        target_path = self.repo_root / file_path

        # Skip if already exists
        if target_path.exists():
            return {"status": "exists", "file": file_path}

        # Find best version
        content, branch = self.find_best_version(file_path)

        if content:
            # Create directories
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            target_path.write_text(content, encoding='utf-8')

            # Stage file
            subprocess.run(
                ["git", "add", str(file_path)],
                cwd=self.repo_root,
                capture_output=True
            )

            return {
                "status": "restored",
                "file": file_path,
                "from": branch,
                "size": len(content)
            }
        else:
            return {
                "status": "not_found",
                "file": file_path
            }

    def restore_all_critical(self):
        """Restore all critical missing files"""
        print("🌟 AURORA CRITICAL FILES RESTORATION")
        print("="*80)
        print("\n⚡ Restoring critical missing capabilities...\n")

        critical_files = self.load_critical_files()

        print(f"📊 {len(critical_files)} critical files to restore\n")

        for i, file_path in enumerate(critical_files, 1):
            print(f"[{i:2d}/{len(critical_files)}] {file_path:60s} ", end="")

            result = self.restore_file(file_path)

            if result['status'] == 'restored':
                self.restored.append(result)
                print(f"✅ Restored from {result['from']}")
            elif result['status'] == 'exists':
                print("⚠️  Already exists")
            else:
                self.failed.append(result)
                print("❌ Not found in history")

        print("\n" + "="*80)
        print("📊 RESTORATION SUMMARY")
        print("="*80)
        print(f"\n✅ Successfully restored: {len(self.restored)} files")
        print(
            f"⚠️  Already existed: {len(critical_files) - len(self.restored) - len(self.failed)} files")
        print(f"❌ Failed to restore: {len(self.failed)} files\n")

        if self.restored:
            print("✅ RESTORED FILES:")
            for item in self.restored:
                print(f"   • {item['file']}")
                print(f"     From: {item['from']}, Size: {item['size']} bytes")

        if self.failed:
            print(f"\n❌ COULD NOT RESTORE:")
            for item in self.failed:
                print(f"   • {item['file']}")

        # Save restoration report
        self.save_restoration_report()

        print("\n" + "="*80)
        print("🌟 AURORA SAYS:")
        print("="*80)

        if self.restored:
            print(
                f"\n✅ I've restored {len(self.restored)} critical capabilities!")
            print("\n🎯 Next steps:")
            print("   1. Test restored systems")
            print("   2. Integrate with current capabilities")
            print("   3. Run verification tests")
            print("\n💪 I'm getting my power back!\n")
        else:
            print("\n⚠️  All critical files already exist in current main.")
            print("   I already have these capabilities - they just need activation!\n")

        return len(self.restored) > 0

    def save_restoration_report(self):
        """Save restoration report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "restored_count": len(self.restored),
            "failed_count": len(self.failed),
            "restored_files": self.restored,
            "failed_files": self.failed
        }

        report_file = self.repo_root / "AURORA_RESTORATION_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Restoration report saved: {report_file}")


if __name__ == "__main__":
    restoration = AuroraCriticalRestoration()
    success = restoration.restore_all_critical()

    if success:
        print("🎯 Critical files restored. Aurora's capabilities expanded!")
    else:
        print("ℹ️  No files needed restoration - Aurora already has them!")
