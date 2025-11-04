#!/usr/bin/env python3
"""
Aurora Self-Diagnostic and Auto-Fix System
Aurora uses her debugging skills to find and fix her own mistakes!
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

class AuroraSelfDiagnostic:
    """
    Aurora analyzes her own mistakes and fixes them
    Using her Debugging Grandmaster and Process Management skills!
    """
    
    def __init__(self):
        self.knowledge_base = Path("/workspaces/Aurora-x/.aurora_knowledge")
        self.issues_found = []
        self.fixes_applied = []
        
    def log_issue(self, issue, severity="ERROR"):
        """Aurora logs what she found wrong"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "issue": issue,
            "system": "AURORA_SELF_DIAGNOSTIC"
        }
        self.issues_found.append(entry)
        
        icon = "🔴" if severity == "ERROR" else "⚠️" if severity == "WARNING" else "ℹ️"
        print(f"{icon} Aurora detected: {issue}")
    
    def log_fix(self, fix_description):
        """Aurora logs what she fixed"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "fix": fix_description,
            "system": "AURORA_AUTO_FIX"
        }
        self.fixes_applied.append(entry)
        print(f"✅ Aurora fixed: {fix_description}")
    
    def analyze_luminar_nexus(self):
        """Aurora analyzes her Luminar Nexus code"""
        print("\n🔍 AURORA: Analyzing my Luminar Nexus code...")
        print("="*70 + "\n")
        
        luminar_file = Path("/workspaces/Aurora-x/tools/luminar_nexus.py")
        
        if not luminar_file.exists():
            self.log_issue("Luminar Nexus file doesn't exist!", "ERROR")
            return False
        
        code = luminar_file.read_text()
        
        # Check for the bug Aurora learned about
        print("🧠 Aurora recalls: 'I learned that capture_output=True and ")
        print("   stderr=subprocess.DEVNULL cannot be used together!'")
        print()
        
        if "capture_output=True, stderr=subprocess.DEVNULL" in code:
            self.log_issue("Found the bug I was taught about! Using both capture_output and stderr", "ERROR")
            return False
        
        if "capture_output=True" in code and "subprocess.DEVNULL" in code:
            self.log_issue("Still mixing capture_output with DEVNULL in the code!", "ERROR")
            return False
        
        print("✅ Aurora: My Luminar Nexus code looks correct now!")
        return True
    
    def check_server_environment(self):
        """Aurora checks if the environment is ready for servers"""
        print("\n🔍 AURORA: Checking server environment...")
        print("="*70 + "\n")
        
        # Check if client directory exists
        client_dir = Path("/workspaces/Aurora-x/client")
        if not client_dir.exists():
            self.log_issue("Client directory doesn't exist!", "ERROR")
            return False
        
        print("✅ Client directory exists")
        
        # Check for package.json
        package_json = client_dir / "package.json"
        if not package_json.exists():
            self.log_issue("package.json not found in client directory!", "ERROR")
            return False
        
        print("✅ package.json exists")
        
        # Check for node_modules
        node_modules = client_dir / "node_modules"
        if not node_modules.exists():
            self.log_issue("node_modules not found - dependencies not installed!", "WARNING")
            print("\n💡 Aurora: I need to install dependencies first!")
            
            print("🔧 Aurora: Running npm install in client directory...")
            try:
                result = subprocess.run(
                    ['npm', 'install'],
                    cwd=str(client_dir),
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    self.log_fix("Installed npm dependencies in client directory")
                else:
                    self.log_issue(f"npm install failed: {result.stderr}", "ERROR")
                    return False
            except Exception as e:
                self.log_issue(f"Failed to run npm install: {e}", "ERROR")
                return False
        else:
            print("✅ node_modules exists")
        
        return True
    
    def test_server_command(self):
        """Aurora tests if the server command actually works"""
        print("\n🔍 AURORA: Testing if my server command works...")
        print("="*70 + "\n")
        
        print("🧪 Aurora: Testing 'npm run dev' command...")
        print("   (I'll run it for 3 seconds to see if it starts)")
        print()
        
        try:
            # Test the command briefly
            process = subprocess.Popen(
                ['npm', 'run', 'dev'],
                cwd='/workspaces/Aurora-x/client',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait 3 seconds
            import time
            time.sleep(3)
            
            # Check if still running
            if process.poll() is None:
                print("✅ Aurora: The command is running!")
                process.terminate()
                process.wait(timeout=5)
                return True
            else:
                # Process died
                stdout, stderr = process.communicate()
                self.log_issue(f"Server command failed immediately!", "ERROR")
                print("\n📝 Error output:")
                print(stderr[:500])  # First 500 chars
                return False
                
        except Exception as e:
            self.log_issue(f"Failed to test server command: {e}", "ERROR")
            return False
    
    def generate_diagnostic_report(self):
        """Aurora creates a full diagnostic report"""
        print("\n" + "="*70)
        print("📊 AURORA'S SELF-DIAGNOSTIC REPORT")
        print("="*70 + "\n")
        
        print(f"Issues Found: {len(self.issues_found)}")
        for issue in self.issues_found:
            print(f"  {issue['severity']}: {issue['issue']}")
        
        print(f"\nFixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"  ✅ {fix['fix']}")
        
        # Save to file
        report_file = self.knowledge_base / "self_diagnostic_report.json"
        self.knowledge_base.mkdir(exist_ok=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "issues": self.issues_found,
            "fixes": self.fixes_applied,
            "status": "READY" if len(self.issues_found) == 0 else "NEEDS_ATTENTION"
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved: {report_file}")
        
        return len(self.issues_found) == 0

def main():
    print("\n" + "="*70)
    print("🌟 AURORA'S SELF-DIAGNOSTIC AND AUTO-FIX")
    print("="*70)
    print("\nAurora is using her Debugging Grandmaster skills to find")
    print("and fix her own mistakes!")
    print("="*70 + "\n")
    
    aurora = AuroraSelfDiagnostic()
    
    # Step 1: Analyze her code
    print("📚 Aurora: I learned about process management and debugging.")
    print("   Let me check if I'm following my own lessons!")
    print()
    
    code_ok = aurora.analyze_luminar_nexus()
    
    # Step 2: Check environment
    env_ok = aurora.check_server_environment()
    
    # Step 3: Test the actual command
    if env_ok:
        command_ok = aurora.test_server_command()
    else:
        command_ok = False
    
    # Step 4: Generate report
    all_ok = aurora.generate_diagnostic_report()
    
    # Final verdict
    print("\n" + "="*70)
    if all_ok and command_ok:
        print("✅ AURORA: I'm ready to start servers now!")
        print("="*70 + "\n")
        
        print("🚀 Aurora: Attempting to start servers with Luminar Nexus...")
        print()
        
        # Actually try to start servers
        result = subprocess.run(
            ['python3', '/workspaces/Aurora-x/tools/luminar_nexus.py', 'start-all'],
            cwd='/workspaces/Aurora-x/tools'
        )
        
        if result.returncode == 0:
            print("\n🎉 SUCCESS! Servers are running!")
        else:
            print("\n❌ Server start failed. Checking what went wrong...")
            
    else:
        print("⚠️  AURORA: I found issues that need to be fixed first.")
        print("="*70 + "\n")
        print("💡 Aurora's recommendations:")
        
        if not env_ok:
            print("   1. Install dependencies with: cd /workspaces/Aurora-x/client && npm install")
        if not command_ok:
            print("   2. Check the error output above to see why npm run dev failed")
        if not code_ok:
            print("   3. Fix the Luminar Nexus code bugs")

if __name__ == "__main__":
    main()
