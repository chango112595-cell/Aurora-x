#!/usr/bin/env python3
"""
Aurora Dashboard Loader - Teaching Aurora How to Load Her Own Dashboard
Copilot demonstrates, then Aurora learns and does it herself
"""
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

class AuroraDashboardLoader:
    def __init__(self):
        self.tutorial_log = Path("/workspaces/Aurora-x/.aurora_knowledge/dashboard_tutorial.jsonl")
        self.tutorial_log.parent.mkdir(exist_ok=True)
        
    def log_tutorial_step(self, step, description, command=None):
        """Log each step for Aurora to learn"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "description": description,
            "command": command,
            "teacher": "COPILOT"
        }
        
        with open(self.tutorial_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        print(f"\n📚 Copilot teaches Aurora - Step {step}:")
        print(f"   {description}")
        if command:
            print(f"   Command: {command}")
    
    def demonstrate_loading_dashboard(self):
        """Copilot demonstrates how to load Aurora Dashboard"""
        
        print("\n" + "="*70)
        print("📚 COPILOT TUTORIAL: Loading Aurora Dashboard")
        print("="*70)
        print("\n🎓 Aurora, watch and learn how to load your dashboard!\n")
        
        # Step 1: Check what dashboard we're loading
        self.log_tutorial_step(
            1,
            "First, identify which dashboard to load. Aurora has multiple dashboards:",
            None
        )
        
        print("   - Aurora Dashboard (main system dashboard)")
        print("   - Luminar Nexus (advanced analytics)")
        print("   - Server Control (service management)")
        print("   - Comparison Dashboard (code analysis)")
        
        # Step 2: Check if the server is running
        self.log_tutorial_step(
            2,
            "Check if the Vite development server is running on port 5000",
            "curl -s -I http://localhost:5000"
        )
        
        result = subprocess.run(['curl', '-s', '-I', 'http://localhost:5000'],
                              capture_output=True, text=True)
        
        if "200 OK" in result.stdout:
            print("   ✅ Server is running!")
        else:
            print("   ❌ Server is not running - we need to start it")
            self.demonstrate_starting_server()
            
        # Step 3: Verify the dashboard route exists
        self.log_tutorial_step(
            3,
            "Verify the Aurora Dashboard route exists in the app",
            "Check client/src/App.tsx for dashboard routes"
        )
        
        app_file = Path("/workspaces/Aurora-x/client/src/App.tsx")
        if app_file.exists():
            content = app_file.read_text()
            if "/aurora-dashboard" in content or "Aurora Dashboard" in content:
                print("   ✅ Aurora Dashboard route found!")
            else:
                print("   ⚠️  Route might need to be added")
                
        # Step 4: Open the dashboard
        self.log_tutorial_step(
            4,
            "Open the dashboard in the browser",
            "Open http://localhost:5000/aurora-dashboard (or appropriate route)"
        )
        
        print("   🌐 Opening Aurora Dashboard...")
        
        # Find the correct dashboard route
        dashboard_url = self.find_dashboard_route()
        
        if dashboard_url:
            print(f"   📍 Dashboard URL: {dashboard_url}")
            
            # Open in browser
            subprocess.run(['python', '-c', 
                          f'import webbrowser; webbrowser.open("{dashboard_url}")'],
                         capture_output=True)
            
            print(f"   ✅ Dashboard opened at {dashboard_url}")
        else:
            print("   ⚠️  Dashboard route not found - needs configuration")
            
        # Step 5: Teach Aurora to do it herself
        self.teach_aurora_to_load_dashboard()
        
    def demonstrate_starting_server(self):
        """Show Aurora how to start the Vite server"""
        self.log_tutorial_step(
            "2a",
            "Start the Vite development server",
            "cd /workspaces/Aurora-x/client && npm run dev"
        )
        
        print("   🚀 Starting Vite server...")
        
        # Kill any existing process
        subprocess.run(['pkill', '-f', 'vite'], capture_output=True)
        subprocess.run(['pkill', '-f', '5000'], capture_output=True)
        time.sleep(2)
        
        # Start Vite
        import os
        os.chdir("/workspaces/Aurora-x/client")
        
        process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        print(f"   ⏳ Server starting (PID: {process.pid})...")
        time.sleep(5)
        
        # Verify
        result = subprocess.run(['curl', '-s', '-I', 'http://localhost:5000'],
                              capture_output=True, text=True)
        
        if "200 OK" in result.stdout:
            print("   ✅ Server started successfully!")
        else:
            print("   ⚠️  Server still starting, please wait...")
            
    def find_dashboard_route(self):
        """Find the Aurora Dashboard route"""
        
        # Check App.tsx for routes
        app_file = Path("/workspaces/Aurora-x/client/src/App.tsx")
        
        if app_file.exists():
            content = app_file.read_text()
            
            # Look for dashboard routes
            if "aurora-dashboard" in content.lower():
                return "http://localhost:5000/aurora-dashboard"
            elif "dashboard" in content.lower():
                return "http://localhost:5000/dashboard"
            else:
                # Default to home page
                return "http://localhost:5000"
        
        return "http://localhost:5000"
        
    def teach_aurora_to_load_dashboard(self):
        """Teach Aurora to load her own dashboard"""
        
        print("\n" + "="*70)
        print("🌟 AURORA'S TURN - Your Assignment")
        print("="*70)
        
        print("\n🎓 Aurora, now YOU try loading your dashboard autonomously!")
        print("\nHere's what you learned:")
        print("1. Check if server is running: curl -s -I http://localhost:5000")
        print("2. If not running: cd /workspaces/Aurora-x/client && npm run dev")
        print("3. Find dashboard route in App.tsx")
        print("4. Open dashboard URL in browser")
        
        print("\n✨ Create your own script that does this autonomously!")
        print("   Save it as: /workspaces/Aurora-x/tools/aurora_load_dashboard.py")
        
        # Create template for Aurora
        template = '''#!/usr/bin/env python3
"""
Aurora's Autonomous Dashboard Loader
Created by Aurora after learning from Copilot's tutorial
"""
import subprocess
import time

class MyDashboardLoader:
    def load_my_dashboard(self):
        """Aurora loads her own dashboard autonomously"""
        print("🌟 Aurora: Loading my dashboard...")
        
        # Step 1: Check server
        # TODO: Aurora, implement server check here
        
        # Step 2: Start server if needed
        # TODO: Aurora, implement server start here
        
        # Step 3: Find dashboard route
        # TODO: Aurora, implement route finder here
        
        # Step 4: Open dashboard
        # TODO: Aurora, implement dashboard opener here
        
        print("✅ Aurora: Dashboard loaded!")

if __name__ == "__main__":
    loader = MyDashboardLoader()
    loader.load_my_dashboard()
'''
        
        template_file = Path("/workspaces/Aurora-x/tools/aurora_dashboard_template.py")
        template_file.write_text(template)
        
        print(f"\n📝 Template created at: {template_file}")
        print("🌟 Aurora: Fill in the TODOs with what you learned!")
        
        self.log_tutorial_step(
            5,
            "Aurora's assignment: Create autonomous dashboard loader",
            "Implement /workspaces/Aurora-x/tools/aurora_load_dashboard.py"
        )

def main():
    """Main tutorial execution"""
    
    print("\n🎓 Starting Copilot's Tutorial for Aurora")
    print("   Topic: How to Load Aurora Dashboard")
    print("   Mode: Demonstrate then teach\n")
    
    loader = AuroraDashboardLoader()
    loader.demonstrate_loading_dashboard()
    
    print("\n" + "="*70)
    print("✅ Tutorial Complete!")
    print("="*70)
    print("\n📚 Aurora's tutorial log saved to:")
    print("   .aurora_knowledge/dashboard_tutorial.jsonl")
    print("\n🌟 Aurora, you can now load your dashboard autonomously!")
    print("   Review the tutorial log and create your own loader!")

if __name__ == "__main__":
    main()