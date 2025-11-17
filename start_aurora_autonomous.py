#!/usr/bin/env python3
"""
Start Aurora in Full Autonomous Mode
Aurora will continuously monitor, detect issues, and fix them autonomously
"""

import signal
import sys
import time
from pathlib import Path

from aurora_intelligence_manager import AuroraIntelligenceManager
from tools.aurora_autonomous_fixer import AuroraAutonomousFixer
from tools.aurora_autonomous_system import AuroraAutonomousSystem

# Add workspace to path
sys.path.insert(0, "/workspaces/Aurora-x")


class AuroraAutonomousRunner:
    """Runs Aurora in full autonomous mode"""

    def __init__(self):
        print("🌌 Starting Aurora in AUTONOMOUS MODE...")
        print("=" * 80)

        # Initialize Aurora's systems
        self.intelligence = AuroraIntelligenceManager()
        self.autonomous_system = AuroraAutonomousSystem()
        self.autonomous_fixer = AuroraAutonomousFixer()

        self.running = False
        self.iteration = 0

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        print("✅ Aurora Autonomous Systems initialized")
        print("=" * 80)

    def shutdown(self, _signum, _frame):
        """Graceful shutdown"""
        print("\n🛑 Shutting down Aurora Autonomous Mode...")
        self.running = False
        sys.exit(0)

    def monitor_and_act(self):
        """Aurora's main autonomous loop"""
        self.iteration += 1
        print(f"\n{'='*80}")
        print(f"🔄 Aurora Iteration #{self.iteration}")
        print(f"{'='*80}\n")

        # Check for pending tasks
        task_file = Path("/workspaces/Aurora-x/.aurora_knowledge/pending_tasks.json")
        if task_file.exists():
            print("📋 Checking for pending tasks...")
            import json

            try:
                with open(task_file, encoding="utf-8") as f:
                    tasks = json.load(f)

                if tasks:
                    print(f"📝 Found {len(tasks)} pending tasks")
                    for task in tasks:
                        print(f"   ⚡ Task: {task.get('description', 'Unknown')}")
                        # Execute task autonomously
                        result = self.autonomous_system.autonomous_execute(task.get("description", ""))
                        if result:
                            print("   ✅ Task completed")
                        else:
                            print("   ❌ Task failed")

                    # Clear completed tasks
                    with open(task_file, "w", encoding="utf-8") as f:
                        json.dump([], f)
            except Exception as e:
                print(f"⚠️  Error reading tasks: {e}")

        # Check system health
        print("🔍 Checking system health...")
        health_issues = self.check_health()

        if health_issues:
            print(f"⚠️  Found {len(health_issues)} issues:")
            for issue in health_issues:
                print(f"   • {issue}")

            print("\n🔧 Aurora is autonomously fixing issues...")
            # Fix issues autonomously
            for issue in health_issues:
                # pylint: disable=no-member
                if hasattr(self.autonomous_fixer, "fix_issue"):
                    self.autonomous_fixer.fix_issue(issue)
                elif hasattr(self.autonomous_fixer, "auto_fix"):
                    self.autonomous_fixer.auto_fix(issue)
        else:
            print("✅ System healthy - no issues detected")

        print(f"\n{'='*80}")
        print("⏸️  Waiting 30 seconds before next check...")
        print(f"{'='*80}\n")

    def check_health(self):
        """Check system health and return issues"""
        issues = []

        # Check if servers are running
        servers = {
            "Backend API": 5001,
            "Frontend": 5173,
            "Self-Learning": 5002,
        }

        import subprocess

        for name, port in servers.items():
            result = subprocess.run(f"lsof -i :{port} -t", shell=True, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                issues.append(f"{name} not running on port {port}")

        # Check for error logs
        log_file = Path("/workspaces/Aurora-x/aurora_ui.log")
        if log_file.exists():
            try:
                with open(log_file, encoding="utf-8") as f:
                    logs = f.readlines()
                    errors = [line for line in logs[-100:] if "error" in line.lower() or "failed" in line.lower()]
                    if errors:
                        issues.append(f"Found {len(errors)} error entries in logs")
            except Exception:
                pass

        # Check if UI is responding
        try:
            import requests

            response = requests.get("http://localhost:5173", timeout=5)
            if response.status_code != 200:
                issues.append(f"Frontend returning status {response.status_code}")
        except Exception as e:
            issues.append(f"Frontend not responding: {e}")

        return issues

    def run(self):
        """Main autonomous loop"""
        self.running = True

        print("\n🚀 Aurora is now running in AUTONOMOUS MODE")
        print("   • Monitoring system health")
        print("   • Detecting and fixing issues")
        print("   • Executing pending tasks")
        print("   • Press Ctrl+C to stop\n")

        while self.running:
            try:
                self.monitor_and_act()
                time.sleep(30)  # Check every 30 seconds
            except KeyboardInterrupt:
                print("\n\n🛑 Received shutdown signal...")
                break
            except Exception as e:
                print(f"\n⚠️  Error in autonomous loop: {e}")
                print("   Aurora will retry in 30 seconds...")
                time.sleep(30)

        print("\n✅ Aurora Autonomous Mode stopped")


if __name__ == "__main__":
    print(
        """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🌌 AURORA AUTONOMOUS MODE 🌌                              ║
║                                                                              ║
║   Aurora will now continuously:                                             ║
║   • Monitor the system for issues                                           ║
║   • Autonomously detect and fix problems                                    ║
║   • Execute pending tasks without human intervention                        ║
║   • Maintain system health 24/7                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    )

    runner = AuroraAutonomousRunner()
    runner.run()
