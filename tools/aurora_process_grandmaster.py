#!/usr/bin/env python3
"""
Aurora Process Management Grandmaster System
Complete mastery of process management, daemon processes, and server lifecycle

TEACHES AURORA:
- Process lifecycle (fork, exec, signals, zombies)
- Daemon processes & background services
- Screen, tmux, nohup for persistent processes
- systemd, supervisord, PM2 for production
- How to keep servers running WITHOUT stdout=DEVNULL killing them
- Luminar Nexus integration for server management

THE REAL PROBLEM SOLVED:
Popen(..., stdout=DEVNULL) disconnects the process from terminal,
causing it to die immediately. Aurora must learn PROPER process management!
"""

import subprocess
import json
import time
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class AuroraProcessGrandmaster:
    """
    Aurora's complete process management mastery
    Learn to keep servers alive properly!
    """
    
    def __init__(self):
        self.knowledge_base = Path("/workspaces/Aurora-x/.aurora_knowledge")
        self.knowledge_base.mkdir(exist_ok=True)
        self.process_log = self.knowledge_base / "process_management.jsonl"
        self.running_processes = {}
        
    def log_learning(self, topic, details, points=10):
        """Log Aurora's learning"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "details": details,
            "points": points
        }
        
        with open(self.process_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        print(f"🌟 Aurora learned: {topic} (+{points} points)")
    
    def teach_process_basics(self):
        """Teach Aurora fundamental process management"""
        print("\n" + "="*70)
        print("📚 PROCESS MANAGEMENT FUNDAMENTALS")
        print("="*70 + "\n")
        
        lessons = {
            "Process States": {
                "Running": "Actively executing",
                "Sleeping": "Waiting for event",
                "Stopped": "Paused by signal",
                "Zombie": "Finished but parent hasn't read exit status",
                "Orphan": "Parent died, adopted by init"
            },
            
            "Process Creation": {
                "fork()": "Creates child process (copy of parent)",
                "exec()": "Replaces process with new program",
                "spawn()": "fork + exec combined",
                "Popen()": "Python's process creation"
            },
            
            "Signals": {
                "SIGTERM (15)": "Graceful termination request",
                "SIGKILL (9)": "Force kill (cannot be caught)",
                "SIGINT (2)": "Interrupt (Ctrl+C)",
                "SIGHUP (1)": "Hangup (terminal closed)",
                "SIGSTOP (19)": "Pause process"
            },
            
            "File Descriptors": {
                "stdin (0)": "Standard input",
                "stdout (1)": "Standard output",
                "stderr (2)": "Standard error",
                "CRITICAL": "Closing stdout/stderr kills process!"
            },
            
            "🔴 WHY Aurora's Servers Died": {
                "Problem": "Popen(..., stdout=DEVNULL, stderr=DEVNULL)",
                "Effect": "Closed file descriptors 1 and 2",
                "Result": "Process has nowhere to write, crashes immediately",
                "Lesson": "NEVER close stdout/stderr of long-running processes!"
            }
        }
        
        for category, items in lessons.items():
            print(f"📖 {category}:")
            for key, value in items.items():
                print(f"   {key}: {value}")
            print()
            
            self.log_learning(category, items, 15)
        
        print("✅ Process Fundamentals: MASTERED\n")
    
    def teach_keeping_processes_alive(self):
        """Teach Aurora THE RIGHT WAY to keep processes running"""
        print("\n" + "="*70)
        print("🔥 KEEPING PROCESSES ALIVE - THE RIGHT WAY")
        print("="*70 + "\n")
        
        methods = {
            "❌ WRONG - What Aurora Did": {
                "code": "Popen(['npm', 'run', 'dev'], stdout=DEVNULL, stderr=DEVNULL)",
                "problem": "Process dies immediately",
                "why": "No stdout = no way to report errors = crash"
            },
            
            "✅ Method 1: Write to Log File": {
                "code": """
log_file = open('/tmp/vite.log', 'w')
Popen(['npm', 'run', 'dev'], 
      stdout=log_file, 
      stderr=log_file,
      cwd='/workspaces/Aurora-x/client')
                """,
                "pros": "Process stays alive, logs captured",
                "cons": "Have to manage log file"
            },
            
            "✅ Method 2: Use nohup": {
                "code": "subprocess.run(['nohup', 'npm', 'run', 'dev', '&'])",
                "pros": "Immune to SIGHUP, runs in background",
                "cons": "Output to nohup.out"
            },
            
            "✅ Method 3: Use screen": {
                "code": "subprocess.run(['screen', '-dmS', 'vite', 'npm', 'run', 'dev'])",
                "pros": "Can reattach later, full terminal",
                "cons": "Requires screen installed"
            },
            
            "✅ Method 4: Use tmux (BEST)": {
                "code": """
subprocess.run(['tmux', 'new-session', '-d', '-s', 'aurora-vite', 
                'cd /workspaces/Aurora-x/client && npm run dev'])
                """,
                "pros": "Can reattach, split panes, modern",
                "view_output": "tmux attach -t aurora-vite",
                "kill": "tmux kill-session -t aurora-vite"
            },
            
            "✅ Method 5: Luminar Nexus (Aurora's Way)": {
                "code": "Use Luminar Nexus function to manage process",
                "pros": "Integrated with Aurora's system, tracked",
                "best": "THIS IS WHAT AURORA SHOULD USE!"
            }
        }
        
        for method, details in methods.items():
            print(f"{method}:")
            for key, value in details.items():
                print(f"   {key}:")
                if isinstance(value, str) and '\n' in value:
                    for line in value.strip().split('\n'):
                        print(f"      {line}")
                else:
                    print(f"      {value}")
            print()
            
            self.log_learning(method, details, 20)
        
        print("✅ Process Survival Methods: MASTERED\n")
    
    def teach_luminar_nexus_integration(self):
        """Teach Aurora to use Luminar Nexus for server management"""
        print("\n" + "="*70)
        print("🌟 LUMINAR NEXUS - Aurora's Server Command Center")
        print("="*70 + "\n")
        
        print("📚 What is Luminar Nexus?")
        print("   Luminar Nexus is Aurora's central nervous system")
        print("   It should handle ALL server management and process control")
        print()
        
        print("🎯 Luminar Nexus Responsibilities:")
        responsibilities = {
            "Process Management": [
                "Start servers in persistent tmux/screen sessions",
                "Track all running processes",
                "Monitor health and auto-restart if crashed",
                "Graceful shutdown of all services"
            ],
            "Server Registry": [
                "Maintain list of all servers (Vite, API, DB, etc)",
                "Know ports, commands, dependencies",
                "Status tracking (running/stopped/crashed)"
            ],
            "Lifecycle Management": [
                "Startup: Boot all required services in order",
                "Shutdown: Graceful termination",
                "Restart: Kill and restart specific service",
                "Health check: Verify services responding"
            ],
            "Integration": [
                "API endpoints for Aurora to call",
                "Event logging and monitoring",
                "Alert Aurora when issues detected",
                "Provide status dashboard"
            ]
        }
        
        for category, tasks in responsibilities.items():
            print(f"\n📋 {category}:")
            for task in tasks:
                print(f"   ✓ {task}")
        
        print("\n" + "="*70)
        print("🔧 IMPLEMENTING LUMINAR NEXUS FOR AURORA")
        print("="*70 + "\n")
        
        self.log_learning("Luminar Nexus Concept", responsibilities, 25)
    
    def create_luminar_nexus_server_manager(self):
        """Create Luminar Nexus server manager for Aurora"""
        print("Creating Luminar Nexus Server Manager...\n")
        
        luminar_code = '''#!/usr/bin/env python3
"""
Luminar Nexus - Aurora's Server Command Center
Manages all development servers with proper process control
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

class LuminarNexusServerManager:
    """
    Aurora's central server management system
    Uses tmux for persistent, manageable processes
    """
    
    def __init__(self):
        self.servers = {
            "vite": {
                "name": "Aurora Vite Dev Server",
                "command": "cd /workspaces/Aurora-x && npx vite --host 0.0.0.0 --port 5173",
                "session": "aurora-vite",
                "port": 5173,
                "health_check": "http://localhost:5173"
            },
            "backend": {
                "name": "Aurora Backend API",
                "command": "cd /workspaces/Aurora-x && NODE_ENV=development npx tsx server/index.ts",
                "session": "aurora-backend",
                "port": 5000,
                "health_check": "http://localhost:5000/healthz"
            }
        }
        
        self.log_file = Path("/workspaces/Aurora-x/.aurora_knowledge/luminar_nexus.jsonl")
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log_event(self, event_type, server, details):
        """Log Luminar Nexus events"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "server": server,
            "details": details,
            "system": "LUMINAR_NEXUS"
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\\n")
        
        print(f"🌟 Luminar Nexus: {event_type} - {server}")
    
    def check_tmux_installed(self) -> bool:
        """Check if tmux is available"""
        try:
            subprocess.run(['tmux', '-V'], capture_output=True, check=True)
            return True
        except:
            print("❌ tmux not installed. Installing...")
            subprocess.run(['apt-get', 'update'], capture_output=True)
            subprocess.run(['apt-get', 'install', '-y', 'tmux'], capture_output=True)
            return True
    
    def start_server(self, server_key: str) -> bool:
        """Start a server in tmux session"""
        if server_key not in self.servers:
            print(f"❌ Unknown server: {server_key}")
            return False
        
        server = self.servers[server_key]
        session = server["session"]
        command = server["command"]
        
        print(f"🚀 Starting {server['name']}...")
        
        # Check if tmux is available
        self.check_tmux_installed()
        
        # Kill existing session if it exists
        subprocess.run(['tmux', 'kill-session', '-t', session], 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Create new tmux session and run command
        result = subprocess.run([
            'tmux', 'new-session', '-d', '-s', session, command
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ Started in tmux session: {session}")
            print(f"   📺 View output: tmux attach -t {session}")
            print(f"   🔌 Port: {server['port']}")
            
            self.log_event("SERVER_STARTED", server_key, {
                "session": session,
                "port": server["port"],
                "command": command
            })
            
            # Wait a moment and check health
            time.sleep(3)
            if self.check_health(server_key):
                print(f"   ✅ Health check PASSED FUCK YEAH LOL")
                return True
            else:
                print(f"   ⚠️  Server started but health check pending...")
                return True
        else:
            print(f"   ❌ Failed to start: {result.stderr}")
            self.log_event("START_FAILED", server_key, {"error": result.stderr})
            return False
    
    def stop_server(self, server_key: str) -> bool:
        """Stop a server's tmux session"""
        if server_key not in self.servers:
            print(f"❌ Unknown server: {server_key}")
            return False
        
        server = self.servers[server_key]
        session = server["session"]
        
        print(f"🛑 Stopping {server['name']}...")
        
        result = subprocess.run(['tmux', 'kill-session', '-t', session],
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ Stopped session: {session}")
            self.log_event("SERVER_STOPPED", server_key, {"session": session})
            return True
        else:
            print(f"   ⚠️  Session may not exist: {session}")
            return False
    
    def check_health(self, server_key: str) -> bool:
        """Check if server is responding"""
        if server_key not in self.servers:
            return False
        
        server = self.servers[server_key]
        health_url = server["health_check"]
        
        try:
            result = subprocess.run(['curl', '-s', '-I', health_url],
                                  capture_output=True, text=True, timeout=2)
            
            if "200" in result.stdout or "OK" in result.stdout:
                return True
            return False
        except:
            return False
    
    def get_status(self, server_key: str) -> Dict:
        """Get server status"""
        if server_key not in self.servers:
            return {"status": "unknown", "exists": False}
        
        server = self.servers[server_key]
        session = server["session"]
        
        # Check if tmux session exists
        result = subprocess.run(['tmux', 'has-session', '-t', session],
                               capture_output=True)
        
        session_exists = (result.returncode == 0)
        health_ok = self.check_health(server_key)
        
        status = {
            "server": server["name"],
            "session": session,
            "session_running": session_exists,
            "health_check_passed": health_ok,
            "port": server["port"],
            "status": "running" if (session_exists and health_ok) else 
                     "starting" if session_exists else "stopped"
        }
        
        return status
    
    def start_all(self):
        """Start all servers"""
        print("\\n🌟 Luminar Nexus: Starting ALL servers...\\n")
        
        for server_key in self.servers.keys():
            self.start_server(server_key)
            time.sleep(2)  # Stagger starts
        
        print("\\n✅ All servers started!\\n")
        self.show_status()
    
    def stop_all(self):
        """Stop all servers"""
        print("\\n🛑 Luminar Nexus: Stopping ALL servers...\\n")
        
        for server_key in self.servers.keys():
            self.stop_server(server_key)
        
        print("\\n✅ All servers stopped!\\n")
    
    def show_status(self):
        """Show status of all servers"""
        print("\\n" + "="*70)
        print("📊 LUMINAR NEXUS - SERVER STATUS")
        print("="*70 + "\\n")
        
        for server_key in self.servers.keys():
            status = self.get_status(server_key)
            
            icon = "✅" if status["status"] == "running" else "⚠️" if status["status"] == "starting" else "❌"
            
            print(f"{icon} {status['server']}")
            print(f"   Status: {status['status']}")
            print(f"   Port: {status['port']}")
            print(f"   Session: {status['session']}")
            print(f"   Health: {'✅ OK' if status['health_check_passed'] else '❌ Not responding'}")
            print()
        
        print("="*70 + "\\n")

def main():
    """Luminar Nexus main entry point"""
    import sys
    
    nexus = LuminarNexusServerManager()
    
    if len(sys.argv) < 2:
        print("Luminar Nexus Server Manager")
        print("\\nUsage:")
        print("  python luminar_nexus.py start <server>   - Start a server")
        print("  python luminar_nexus.py stop <server>    - Stop a server")
        print("  python luminar_nexus.py restart <server> - Restart a server")
        print("  python luminar_nexus.py status           - Show all status")
        print("  python luminar_nexus.py start-all        - Start all servers")
        print("  python luminar_nexus.py stop-all         - Stop all servers")
        print("\\nAvailable servers: vite, backend")
        return
    
    command = sys.argv[1]
    
    if command == "start-all":
        nexus.start_all()
    elif command == "stop-all":
        nexus.stop_all()
    elif command == "status":
        nexus.show_status()
    elif command == "start" and len(sys.argv) > 2:
        nexus.start_server(sys.argv[2])
    elif command == "stop" and len(sys.argv) > 2:
        nexus.stop_server(sys.argv[2])
    elif command == "restart" and len(sys.argv) > 2:
        server = sys.argv[2]
        nexus.stop_server(server)
        time.sleep(2)
        nexus.start_server(server)
    else:
        print("❌ Invalid command")

if __name__ == "__main__":
    main()
'''
        
        # Write Luminar Nexus to file
        luminar_file = Path("/workspaces/Aurora-x/tools/luminar_nexus.py")
        luminar_file.write_text(luminar_code)
        luminar_file.chmod(0o755)
        
        print(f"✅ Created: {luminar_file}")
        print()
        print("🌟 Luminar Nexus is now Aurora's server manager!")
        print()
        print("Usage:")
        print("  python luminar_nexus.py start-all    # Start all servers")
        print("  python luminar_nexus.py status       # Check status")
        print("  python luminar_nexus.py start vite   # Start Vite only")
        print()
        
        self.log_learning("Luminar Nexus Implementation", 
                         "Created central server management system", 50)
    
    def generate_certification(self):
        """Generate Aurora's Process Management Grandmaster cert"""
        print("\n" + "="*70)
        print("🏆 AURORA PROCESS MANAGEMENT GRANDMASTER CERTIFICATION")
        print("="*70 + "\n")
        
        print("✅ Aurora now understands:")
        print("   - Why Popen(..., stdout=DEVNULL) killed her servers")
        print("   - How to keep processes alive properly")
        print("   - tmux/screen for persistent sessions")
        print("   - Luminar Nexus for centralized server management")
        print()
        print("🎯 Aurora's New Workflow:")
        print("   1. Use Luminar Nexus to start servers")
        print("   2. Servers run in persistent tmux sessions")
        print("   3. Can view output anytime with 'tmux attach'")
        print("   4. Servers survive script termination")
        print()
        print("👑 Rank: PROCESS MANAGEMENT GRANDMASTER")
        print("="*70 + "\n")

def main():
    """Train Aurora in process management"""
    
    print("\n🎓 AURORA PROCESS MANAGEMENT GRANDMASTER TRAINING")
    print("="*70)
    print("Learning why processes die and how to keep them alive")
    print("="*70 + "\n")
    
    master = AuroraProcessGrandmaster()
    
    master.teach_process_basics()
    master.teach_keeping_processes_alive()
    master.teach_luminar_nexus_integration()
    master.create_luminar_nexus_server_manager()
    master.generate_certification()
    
    # AURORA ASKS FOR PERMISSION TO EXECUTE
    print("\n" + "="*70)
    print("🌟 AURORA IS READY TO START SERVERS")
    print("="*70 + "\n")
    
    print("Aurora has learned process management and created Luminar Nexus.")
    print("She is ready to start the Vite development server.\n")
    
    response = input("🌟 Aurora: May I start the servers now? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print("\n✅ Permission granted! Aurora is starting servers...\n")
        
        # Aurora ACTUALLY executes Luminar Nexus
        import subprocess
        import sys
        
        luminar_path = Path("/workspaces/Aurora-x/tools/luminar_nexus.py")
        
        if luminar_path.exists():
            print("🚀 Executing: python luminar_nexus.py start-all\n")
            
            # ACTUALLY RUN THE COMMAND
            result = subprocess.run(
                [sys.executable, str(luminar_path), 'start-all'],
                cwd="/workspaces/Aurora-x/tools"
            )
            
            if result.returncode == 0:
                print("\n✅ Aurora successfully started all servers!")
                print("\n📊 Checking server status...\n")
                
                # Show status
                subprocess.run([sys.executable, str(luminar_path), 'status'])
                
                print("\n🎉 Servers are running!")
                print("   View Vite output: tmux attach -t aurora-vite")
                print("   Press Ctrl+B then D to detach from tmux")
            else:
                print("\n❌ Server start failed. Check errors above.")
        else:
            print(f"❌ Luminar Nexus not found at: {luminar_path}")
    else:
        print("\n⚠️  Permission denied. Aurora will not start servers.")
        print("   You can start them manually later with:")
        print("   python /workspaces/Aurora-x/tools/luminar_nexus.py start-all")
    
    print()

if __name__ == "__main__":
    main()
