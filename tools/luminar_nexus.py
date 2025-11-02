#!/usr/bin/env python3
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
                "command": "cd /workspaces/Aurora-x/client && npm run dev",
                "session": "aurora-vite",
                "port": 5173,
                "health_check": "http://localhost:5173"
            },
            "backend": {
                "name": "Aurora Backend API",
                "command": "cd /workspaces/Aurora-x && npm run server",
                "session": "aurora-api",
                "port": 5001,
                "health_check": "http://localhost:5001/health"
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
            f.write(json.dumps(entry) + "\n")
        
        print(f"🌟 Luminar Nexus: {event_type} - {server}")
    
    def check_tmux_installed(self) -> bool:
        """Check if tmux is available"""
        try:
            subprocess.run(['tmux', '-V'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except:
            print("❌ tmux not installed. Installing...")
            subprocess.run(['apt-get', 'update'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(['apt-get', 'install', '-y', 'tmux'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
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
                print(f"   ✅ Health check PASSED")
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
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
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
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2)
            
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
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
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
        print("\n🌟 Luminar Nexus: Starting ALL servers...\n")
        
        for server_key in self.servers.keys():
            self.start_server(server_key)
            time.sleep(2)  # Stagger starts
        
        print("\n✅ All servers started!\n")
        self.show_status()
    
    def stop_all(self):
        """Stop all servers"""
        print("\n🛑 Luminar Nexus: Stopping ALL servers...\n")
        
        for server_key in self.servers.keys():
            self.stop_server(server_key)
        
        print("\n✅ All servers stopped!\n")
    
    def show_status(self):
        """Show status of all servers"""
        print("\n" + "="*70)
        print("📊 LUMINAR NEXUS - SERVER STATUS")
        print("="*70 + "\n")
        
        for server_key in self.servers.keys():
            status = self.get_status(server_key)
            
            icon = "✅" if status["status"] == "running" else "⚠️" if status["status"] == "starting" else "❌"
            
            print(f"{icon} {status['server']}")
            print(f"   Status: {status['status']}")
            print(f"   Port: {status['port']}")
            print(f"   Session: {status['session']}")
            print(f"   Health: {'✅ OK' if status['health_check_passed'] else '❌ Not responding'}")
            print()
        
        print("="*70 + "\n")

def main():
    """Luminar Nexus main entry point"""
    import sys
    
    nexus = LuminarNexusServerManager()
    
    if len(sys.argv) < 2:
        print("Luminar Nexus Server Manager")
        print("\nUsage:")
        print("  python luminar_nexus.py start <server>   - Start a server")
        print("  python luminar_nexus.py stop <server>    - Stop a server")
        print("  python luminar_nexus.py restart <server> - Restart a server")
        print("  python luminar_nexus.py status           - Show all status")
        print("  python luminar_nexus.py start-all        - Start all servers")
        print("  python luminar_nexus.py stop-all         - Stop all servers")
        print("\nAvailable servers: vite, backend")
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
