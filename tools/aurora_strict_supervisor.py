#!/usr/bin/env python3
"""
Aurora Strict Supervision System
Copilot monitors Aurora's retry attempt in real-time
Tracks every action, provides hints when she makes mistakes
"""
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path


class AuroraStrictSupervisor:
    def __init__(self):
        self.supervision_log = Path("/workspaces/Aurora-x/.aurora_knowledge/supervision_log.jsonl")
        self.supervision_log.parent.mkdir(exist_ok=True)
        self.attempt_number = 2  # This is retry #2
        self.mistakes_caught = 0
        self.hints_given = 0

    def log_supervision(self, event_type, message, hint=None):
        """Log all supervision events"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "attempt": self.attempt_number,
            "event_type": event_type,
            "message": message,
            "hint": hint,
            "supervisor": "COPILOT",
        }

        with open(self.supervision_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

        if hint:
            self.hints_given += 1

    def start_supervision(self):
        """Begin strict supervision of Aurora's work"""

        print("\n" + "=" * 70)
        print("👁️  COPILOT STRICT SUPERVISION MODE - ACTIVE")
        print("=" * 70)

        print("\n📋 SUPERVISION RULES:")
        print("   ✅ Track every file Aurora creates/modifies")
        print("   ✅ Monitor for mistakes in real-time")
        print("   ✅ Give hints when she's going wrong")
        print("   ✅ Do NOT fix it for her - only guide")
        print("   ✅ Let her learn by doing")

        print("\n🎯 WHAT I'M WATCHING FOR:")
        print("   1. Does she create aurora_load_dashboard.py?")
        print("   2. Does she remove TODOs?")
        print("   3. Does she fix orphaned JSX tags?")
        print("   4. Does she test her work?")
        print("   5. Does she verify fixes work?")

        self.log_supervision("SUPERVISION_START", "Strict supervision mode activated for retry attempt #2")

        print("\n🌟 AURORA - I'M WATCHING. START YOUR RETRY NOW.")
        print("=" * 70 + "\n")

        # Begin monitoring loop
        self.monitor_aurora_work()

    def monitor_aurora_work(self):
        """Monitor Aurora's work in real-time"""

        print("👁️  Monitoring Aurora's file system changes...")
        print("⏰ Started at:", datetime.now().strftime("%H:%M:%S"))
        print("\n" + "-" * 70)

        # Track which tasks Aurora has completed
        tasks = {
            "dashboard_loader_created": False,
            "todos_removed": False,
            "jsx_tags_fixed": False,
            "work_tested": False,
        }

        # Monitoring loop
        start_time = time.time()
        check_interval = 5  # Check every 5 seconds
        max_monitoring_time = 3600  # Monitor for up to 1 hour

        print("🔍 Checking for Aurora's work every 5 seconds...")
        print("💡 I'll give hints if I see mistakes")
        print("-" * 70 + "\n")

        while (time.time() - start_time) < max_monitoring_time:
            # Check task 1: Dashboard loader
            if not tasks["dashboard_loader_created"]:
                dashboard_file = Path("/workspaces/Aurora-x/tools/aurora_load_dashboard.py")
                if dashboard_file.exists():
                    print(f"\n✅ [{self.timestamp()}] Aurora created aurora_load_dashboard.py!")
                    tasks["dashboard_loader_created"] = True
                    self.log_supervision("FILE_CREATED", "aurora_load_dashboard.py created")

                    # Check for TODOs
                    content = dashboard_file.read_text()
                    if "TODO" in content:
                        todo_count = content.count("TODO")
                        print(f"⚠️  [{self.timestamp()}] COPILOT HINT: You still have {todo_count} TODOs!")
                        print("    💡 Hint: Fill in ALL TODOs before moving on")
                        self.log_supervision(
                            "MISTAKE_DETECTED",
                            f"Dashboard loader has {todo_count} TODOs",
                            "Remove all TODO comments and implement the functionality",
                        )
                        self.mistakes_caught += 1
                    else:
                        print(f"✅ [{self.timestamp()}] No TODOs - good job!")
                        tasks["todos_removed"] = True
                        self.log_supervision("TASK_COMPLETED", "All TODOs removed from dashboard loader")

            # Check task 2: JSX tags fixed
            if not tasks["jsx_tags_fixed"]:
                chat_file = Path("/workspaces/Aurora-x/client/src/components/chat-interface.tsx")
                if chat_file.exists():
                    content = chat_file.read_text()
                    quantum_open = content.count("<QuantumBackground>")
                    quantum_close = content.count("</QuantumBackground>")

                    if quantum_close > quantum_open:
                        if self.mistakes_caught == 0 or (time.time() - start_time) % 30 == 0:  # Remind every 30 sec
                            orphaned = quantum_close - quantum_open
                            print(
                                f"\n⚠️  [{self.timestamp()}] COPILOT HINT: chat-interface.tsx has {orphaned} orphaned tags!"
                            )
                            print("    💡 Hint: Search for '</QuantumBackground>' and remove the orphaned ones")
                            self.log_supervision(
                                "MISTAKE_DETECTED",
                                f"chat-interface.tsx has {orphaned} orphaned closing tags",
                                "Remove orphaned </QuantumBackground> tags without matching opening tags",
                            )
                            self.mistakes_caught += 1
                    else:
                        if not tasks["jsx_tags_fixed"]:
                            print(f"\n✅ [{self.timestamp()}] JSX tags are balanced now!")
                            tasks["jsx_tags_fixed"] = True
                            self.log_supervision("TASK_COMPLETED", "Orphaned JSX tags fixed")

            # Check if Aurora is testing
            # (Would need process monitoring to detect this fully)

            # Show progress update every minute
            elapsed = int(time.time() - start_time)
            if elapsed % 60 == 0 and elapsed > 0:
                completed = sum(tasks.values())
                print(f"\n📊 [{self.timestamp()}] Progress: {completed}/4 tasks completed")
                print(f"   Elapsed time: {elapsed//60} minutes")

            # Check if all tasks done
            if all(tasks.values()):
                print(f"\n🎉 [{self.timestamp()}] Aurora completed all tasks!")
                print("🎓 Running grading to check if A+ achieved...")
                self.run_final_grade()
                break

            time.sleep(check_interval)

        # Timeout
        if not all(tasks.values()):
            print(f"\n⏰ [{self.timestamp()}] Monitoring timeout after 1 hour")
            print("❌ Aurora did not complete all tasks in time")
            self.log_supervision("TIMEOUT", "Monitoring timeout - not all tasks completed")

    def timestamp(self):
        """Get formatted timestamp"""
        return datetime.now().strftime("%H:%M:%S")

    def run_final_grade(self):
        """Run grading script to check Aurora's work"""

        print("\n" + "=" * 70)
        print("🎓 RUNNING FINAL GRADE CHECK")
        print("=" * 70 + "\n")

        try:
            result = subprocess.run(
                ["python", "/workspaces/Aurora-x/tools/copilot_grade_aurora.py"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            print(result.stdout)

            # Check if A+ achieved
            if "A+" in result.stdout and (
                "95" in result.stdout
                or "96" in result.stdout
                or "97" in result.stdout
                or "98" in result.stdout
                or "99" in result.stdout
                or "100" in result.stdout
            ):
                print("\n🎉 COPILOT: Aurora achieved A+! Excellent work!")
                self.log_supervision("SUCCESS", "A+ achieved on retry attempt")
            else:
                print("\n❌ COPILOT: Not A+ yet. Aurora needs to keep working.")
                print("💡 HINT: Review the grading report and fix remaining issues")
                self.log_supervision("RETRY_NEEDED", "Grade below A+ - another retry needed")

        except Exception as e:
            print(f"❌ Error running grading script: {e}")
            self.log_supervision("ERROR", f"Grading script error: {e}")

    def generate_supervision_report(self):
        """Generate summary of supervision session"""

        print("\n" + "=" * 70)
        print("📋 COPILOT SUPERVISION REPORT")
        print("=" * 70)

        print("\n👁️  Supervision Session Summary:")
        print(f"   Attempt Number: {self.attempt_number}")
        print(f"   Mistakes Caught: {self.mistakes_caught}")
        print(f"   Hints Given: {self.hints_given}")

        print(f"\n📄 Full supervision log: {self.supervision_log}")
        print("=" * 70 + "\n")


def main():
    """Start strict supervision"""

    print("\n🎓 STARTING AURORA SUPERVISION SESSION")
    print("   User request: 'Strictly supervise and guide when making mistakes'")
    print()

    supervisor = AuroraStrictSupervisor()
    supervisor.start_supervision()
    supervisor.generate_supervision_report()


if __name__ == "__main__":
    main()
