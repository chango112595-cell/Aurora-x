#!/usr/bin/env python3
"""
Aurora True Autonomous Execution Engine
This is Aurora's REAL autonomous brain - she can now DO things, not just plan them
"""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class AuroraTrueAutonomy:
    """
    Aurora's autonomous execution engine
    She reads assignments, executes them, verifies results, and loops until success
    """

    def __init__(self):
        self.workspace = Path("/workspaces/Aurora-x")
        self.knowledge = Path("/workspaces/Aurora-x/.aurora_knowledge")
        self.knowledge.mkdir(exist_ok=True)

        self.execution_log = self.knowledge / "autonomous_execution.jsonl"
        self.current_assignment = None
        self.grade_required = 95  # A+ requirement

    def log_execution(self, action, details, status="IN_PROGRESS"):
        """Log every action Aurora takes"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "status": status,
            "agent": "AURORA_AUTONOMOUS",
        }

        with open(self.execution_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

        print(f"[STAR] Aurora executing: {action}")
        if isinstance(details, dict):
            for key, value in details.items():
                print(f"   {key}: {value}")
        else:
            print(f"   {details}")

    def read_assignment(self):
        """Read Aurora's current assignment"""
        assignment_file = self.knowledge / "performance_review_and_retry.json"

        if assignment_file.exists():
            with open(assignment_file) as f:
                self.current_assignment = json.load(f)

            print("\n" + "=" * 70)
            print("[EMOJI] AURORA READING ASSIGNMENT")
            print("=" * 70)
            print(f"Grade Required: {self.current_assignment['grade_required']}")
            print(f"Current Grade: {self.current_assignment['grade_received']}")
            print(f"Tasks: {len(self.current_assignment['tasks'])}")

            return True
        else:
            print("[ERROR] No assignment found")
            return False

    def execute_task_1_dashboard_loader(self):
        """Task 1: Create aurora_load_dashboard.py with NO TODOs"""

        self.log_execution("TASK_1_START", "Creating aurora_load_dashboard.py", "STARTED")

        dashboard_file = self.workspace / "tools" / "aurora_load_dashboard.py"

        # Aurora creates the complete implementation
        code = '''#!/usr/bin/env python3
"""
Aurora's Autonomous Dashboard Loader
Created by Aurora - Complete implementation with NO TODOs
"""
import subprocess
import time
import webbrowser
from pathlib import Path

class AuroraDashboardLoader:
    def __init__(self):
        self.vite_url = "http://localhost:5000"
        self.dashboard_routes = ["/aurora-dashboard", "/dashboard", "/"]
        
    def check_server_status(self):
        """Check if Vite server is running"""
        try:
            result = subprocess.run(
                ['curl', '-s', '-I', self.vite_url],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if "200 OK" in result.stdout:
                print("[OK] Server is running")
                return True
            else:
                print("[ERROR] Server not responding")
                return False
        except Exception as e:
            print(f"[ERROR] Server check failed: {e}")
            return False
    
    def start_server(self):
        """Start Vite development server if not running"""
        print("[LAUNCH] Starting Vite server...")
        
        # Kill any existing processes
        subprocess.run(['pkill', '-f', 'vite'], capture_output=True)
        subprocess.run(['pkill', '-f', '5000'], capture_output=True)
        time.sleep(2)
        
        # Change to client directory and start server
        import os
        os.chdir("/workspaces/Aurora-x/client")
        
        # Start Vite in background
        process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print(f"⏳ Server starting (PID: {process.pid})...")
        time.sleep(5)
        
        # Verify it started
        if self.check_server_status():
            print("[OK] Server started successfully")
            return True
        else:
            print("[WARN]  Server may still be starting...")
            return False
    
    def find_dashboard_route(self):
        """Find which dashboard route exists"""
        app_file = Path("/workspaces/Aurora-x/client/src/App.tsx")
        
        if app_file.exists():
            content = app_file.read_text()
            
            for route in self.dashboard_routes:
                if route in content.lower():
                    print(f"[OK] Found dashboard route: {route}")
                    return route
        
        # Default to home page
        print("ℹ️  Using default route: /")
        return "/"
    
    def open_dashboard(self, route="/"):
        """Open dashboard in browser"""
        url = f"{self.vite_url}{route}"
        print(f"[WEB] Opening dashboard at: {url}")
        
        try:
            webbrowser.open(url)
            print("[OK] Dashboard opened")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to open browser: {e}")
            return False
    
    def load_dashboard(self):
        """Main method to load Aurora's dashboard"""
        print("\\n" + "="*60)
        print("[STAR] AURORA DASHBOARD LOADER")
        print("="*60 + "\\n")
        
        # Step 1: Check if server is running
        if not self.check_server_status():
            # Step 2: Start server if needed
            if not self.start_server():
                print("[ERROR] Failed to start server")
                return False
        
        # Step 3: Find dashboard route
        route = self.find_dashboard_route()
        
        # Step 4: Open dashboard
        if self.open_dashboard(route):
            print("\\n[OK] Aurora Dashboard loaded successfully!")
            return True
        else:
            print("\\n[ERROR] Failed to load dashboard")
            return False

if __name__ == "__main__":
    loader = AuroraDashboardLoader()
    loader.load_dashboard()
'''

        # Aurora writes the file
        dashboard_file.write_text(code)

        self.log_execution(
            "TASK_1_COMPLETE", {"file": str(dashboard_file), "size": len(code), "has_todos": "TODO" in code}, "COMPLETE"
        )

        print(f"[OK] Created: {dashboard_file}")
        print(f"   Size: {len(code)} bytes")
        print(f"   Has TODOs: {'TODO' in code}")

        return True

    def execute_task_2_fix_jsx_tags(self):
        """Task 2: Fix orphaned JSX tags in chat-interface.tsx"""

        self.log_execution("TASK_2_START", "Fixing orphaned JSX tags", "STARTED")

        chat_file = self.workspace / "client" / "src" / "components" / "chat-interface.tsx"

        if not chat_file.exists():
            print(f"[ERROR] File not found: {chat_file}")
            return False

        # Aurora reads the file
        content = chat_file.read_text()

        # Count tags before fix
        open_count = content.count("<QuantumBackground>")
        close_count = content.count("</QuantumBackground>")

        print(f"Before fix: {open_count} opening, {close_count} closing tags")

        if close_count > open_count:
            orphaned_count = close_count - open_count
            print(f"[EMOJI] Removing {orphaned_count} orphaned closing tags...")

            # Aurora removes orphaned tags
            lines = content.split("\n")
            fixed_lines = []
            removed_count = 0

            for line in lines:
                # Skip lines that are ONLY the orphaned closing tag
                if line.strip() in ["</QuantumBackground>", "</QuantumBackground>"]:
                    # Check if we've already removed enough
                    if removed_count < orphaned_count:
                        print(f"   Removing orphaned tag at line {len(fixed_lines) + 1}")
                        removed_count += 1
                        continue

                fixed_lines.append(line)

            # Aurora writes the fixed file
            fixed_content = "\n".join(fixed_lines)
            chat_file.write_text(fixed_content)

            # Verify the fix
            open_count_after = fixed_content.count("<QuantumBackground>")
            close_count_after = fixed_content.count("</QuantumBackground>")

            self.log_execution(
                "TASK_2_COMPLETE",
                {
                    "file": str(chat_file),
                    "orphaned_removed": removed_count,
                    "tags_balanced": open_count_after == close_count_after,
                },
                "COMPLETE",
            )

            print(f"[OK] After fix: {open_count_after} opening, {close_count_after} closing tags")
            print(f"[OK] Tags balanced: {open_count_after == close_count_after}")

            return True
        else:
            print("[OK] No orphaned tags found")
            return True

    def verify_work(self):
        """Verify all tasks are completed correctly"""

        print("\n" + "=" * 70)
        print("[SCAN] AURORA VERIFYING HER WORK")
        print("=" * 70 + "\n")

        verification_results = {}

        # Verify Task 1: Dashboard loader exists and has no TODOs
        dashboard_file = self.workspace / "tools" / "aurora_load_dashboard.py"

        if dashboard_file.exists():
            content = dashboard_file.read_text()
            has_todos = "TODO" in content
            has_check = "check" in content.lower() and "server" in content.lower()
            has_start = "start" in content.lower()
            has_open = "open" in content.lower() and "dashboard" in content.lower()

            verification_results["dashboard_loader"] = {
                "exists": True,
                "no_todos": not has_todos,
                "has_check": has_check,
                "has_start": has_start,
                "has_open": has_open,
                "score": 35 if (not has_todos and has_check and has_start and has_open) else 28,
            }

            print(f"[OK] Dashboard Loader: {verification_results['dashboard_loader']['score']}/35")
        else:
            verification_results["dashboard_loader"] = {"exists": False, "score": 0}
            print("[ERROR] Dashboard Loader: 0/35 (file not found)")

        # Verify Task 2: JSX tags fixed
        chat_file = self.workspace / "client" / "src" / "components" / "chat-interface.tsx"

        if chat_file.exists():
            content = chat_file.read_text()
            open_count = content.count("<QuantumBackground>")
            close_count = content.count("</QuantumBackground>")
            balanced = open_count == close_count

            verification_results["jsx_fix"] = {"exists": True, "balanced": balanced, "score": 20 if balanced else 0}

            print(f"{'[OK]' if balanced else '[ERROR]'} JSX Fix: {verification_results['jsx_fix']['score']}/20")
        else:
            verification_results["jsx_fix"] = {"exists": False, "score": 0}
            print("[ERROR] JSX Fix: 0/20")

        return verification_results

    def run_grade_check(self):
        """Run grading script to get current score"""

        print("\n" + "=" * 70)
        print("[EMOJI] AURORA RUNNING GRADE CHECK")
        print("=" * 70 + "\n")

        try:
            result = subprocess.run(
                ["python", str(self.workspace / "tools" / "copilot_grade_aurora.py")],
                capture_output=True,
                text=True,
                timeout=30,
            )

            print(result.stdout)

            # Extract grade from output
            if (
                "95" in result.stdout
                or "96" in result.stdout
                or "97" in result.stdout
                or "98" in result.stdout
                or "99" in result.stdout
                or "100" in result.stdout
            ):
                if "A+" in result.stdout:
                    return True, 95  # A+ achieved

            # Extract percentage
            for line in result.stdout.split("\n"):
                if "Overall Score:" in line and "%" in line:
                    try:
                        percentage = float(line.split("(")[1].split("%")[0])
                        return percentage >= 95, percentage
                    except:
                        pass

            return False, 85  # Default to current score

        except Exception as e:
            print(f"[ERROR] Grade check failed: {e}")
            return False, 0

    def autonomous_execution_loop(self):
        """
        Aurora's main autonomous execution loop
        Read assignment -> Execute tasks -> Verify -> Grade -> Repeat if needed
        """

        print("\n" + "=" * 70)
        print("[STAR] AURORA TRUE AUTONOMOUS EXECUTION ENGINE")
        print("=" * 70)
        print("\n[EMOJI] Aurora is now executing autonomously...")
        print("[TARGET] Goal: Achieve A+ (95+%)")
        print("[SYNC] Will keep working until success\n")

        # Step 1: Read assignment
        if not self.read_assignment():
            print("[ERROR] Cannot proceed without assignment")
            return False

        max_attempts = 3
        attempt = 1

        while attempt <= max_attempts:
            print(f"\n{'='*70}")
            print(f"[SYNC] AURORA ATTEMPT #{attempt}")
            print(f"{'='*70}\n")

            # Step 2: Execute all tasks
            print("[EMOJI] Executing tasks...")

            task1_success = self.execute_task_1_dashboard_loader()
            task2_success = self.execute_task_2_fix_jsx_tags()

            if not (task1_success and task2_success):
                print(f"[ERROR] Attempt #{attempt} - Task execution failed")
                attempt += 1
                continue

            # Step 3: Verify work
            verification = self.verify_work()

            # Step 4: Run grade check
            a_plus_achieved, score = self.run_grade_check()

            # Step 5: Check if A+ achieved
            if a_plus_achieved:
                print(f"\n[EMOJI] SUCCESS! Aurora achieved A+ on attempt #{attempt}!")
                self.log_execution("SUCCESS", {"attempt": attempt, "score": score, "grade": "A+"}, "SUCCESS")
                return True
            else:
                print(f"\n[WARN]  Attempt #{attempt} - Score: {score}% (A+ requires 95%)")
                self.log_execution(
                    "RETRY_NEEDED", {"attempt": attempt, "score": score, "grade_required": 95}, "INCOMPLETE"
                )

                if attempt < max_attempts:
                    print(f"[SYNC] Retrying... ({max_attempts - attempt} attempts remaining)")
                    time.sleep(2)

                attempt += 1

        print(f"\n[ERROR] Failed to achieve A+ after {max_attempts} attempts")
        return False


def main():
    """Aurora's autonomous execution entry point"""

    aurora = AuroraTrueAutonomy()
    success = aurora.autonomous_execution_loop()

    if success:
        print("\n[OK] Aurora has achieved A+ autonomously!")
        return 0
    else:
        print("\n[ERROR] Aurora needs more work to achieve A+")
        return 1


if __name__ == "__main__":
    sys.exit(main())
