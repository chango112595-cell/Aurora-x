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
            "bridge": {
                "name": "Aurora Bridge Service (Factory NL→Project)",
                "command_template": "cd /workspaces/Aurora-x && python3 -m aurora_x.bridge.service",
                "session": "aurora-bridge",
                "preferred_port": 5001,
                "port": None,  # Will be assigned dynamically
                "health_check_template": "http://localhost:{port}/healthz"
            },
            "backend": {
                "name": "Aurora Backend API (Main Server)",
                "command_template": "cd /workspaces/Aurora-x && NODE_ENV=development npx tsx server/index.ts",
                "session": "aurora-backend",
                "preferred_port": 5000,
                "port": None,
                "health_check_template": "http://localhost:{port}/healthz"
            },
            "vite": {
                "name": "Aurora Vite Dev Server (Frontend)",
                "command_template": "cd /workspaces/Aurora-x && npx vite --host 0.0.0.0 --port {port}",
                "session": "aurora-vite",
                "preferred_port": 5173,
                "port": None,
                "health_check_template": "http://localhost:{port}"
            },
            "self-learn": {
                "name": "Aurora Self-Learning Server (Continuous Learning)",
                "command_template": "cd /workspaces/Aurora-x && python3 -c 'from aurora_x.self_learn_server import app; import uvicorn; uvicorn.run(app, host=\"0.0.0.0\", port={port})'",
                "session": "aurora-self-learn",
                "preferred_port": 5002,
                "port": None,
                "health_check_template": "http://localhost:{port}/healthz"
            }
        }
        
        self.log_file = Path("/workspaces/Aurora-x/.aurora_knowledge/luminar_nexus.jsonl")
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Intelligently assign ports on initialization
        self._auto_assign_ports()
    
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
    
    def _get_listening_ports(self) -> set:
        """Get all ports currently in use"""
        try:
            result = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True)
            ports = set()
            for line in result.stdout.split('\n'):
                if ':' in line and 'LISTEN' in line:
                    try:
                        # Extract port number from lines like "0.0.0.0:5000"
                        port_part = line.split()[3]
                        port = int(port_part.split(':')[-1])
                        ports.add(port)
                    except:
                        continue
            return ports
        except:
            # Fallback to lsof if ss not available
            try:
                result = subprocess.run(['lsof', '-i', '-P', '-n'], capture_output=True, text=True)
                ports = set()
                for line in result.stdout.split('\n'):
                    if 'LISTEN' in line:
                        try:
                            port = int(line.split(':')[-1].split()[0])
                            ports.add(port)
                        except:
                            continue
                return ports
            except:
                return set()
    
    def _find_available_port(self, preferred_port: int, start_range: int = 5000, end_range: int = 6000) -> int:
        """Find an available port, preferring the suggested port"""
        listening_ports = self._get_listening_ports()
        
        # Try preferred port first
        if preferred_port not in listening_ports:
            return preferred_port
        
        # Find next available port in range
        for port in range(start_range, end_range):
            if port not in listening_ports:
                print(f"   ⚠️  Port {preferred_port} in use, assigned {port} instead")
                return port
        
        raise Exception(f"No available ports in range {start_range}-{end_range}")
    
    def _auto_assign_ports(self):
        """Intelligently assign ports to all servers, avoiding conflicts"""
        print("🔍 Analyzing port availability...")
        
        listening_ports = self._get_listening_ports()
        assigned_ports = set()
        
        for server_key, config in self.servers.items():
            # Find available port
            preferred = config["preferred_port"]
            
            # Check if preferred port is available (not in use AND not already assigned)
            if preferred in listening_ports or preferred in assigned_ports:
                # Find next available
                available_port = self._find_available_port(preferred)
                # Make sure we don't assign something already assigned this session
                while available_port in assigned_ports:
                    available_port += 1
            else:
                available_port = preferred
            
            # Assign port and generate command/health_check from templates
            config["port"] = available_port
            config["command"] = config["command_template"].format(port=available_port)
            config["health_check"] = config["health_check_template"].format(port=available_port)
            
            assigned_ports.add(available_port)
            
            if available_port != config["preferred_port"]:
                self.log_event("PORT_REASSIGNED", server_key, {
                    "preferred": config["preferred_port"],
                    "assigned": available_port,
                    "reason": "port_conflict"
                })
        
        print(f"✅ Port assignment complete: {len(assigned_ports)} ports allocated")
    
    
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
        """Check if server is responding - tries multiple health check patterns"""
        if server_key not in self.servers:
            return False
        
        server = self.servers[server_key]
        base_url = server["health_check"]
        
        # Try multiple health check patterns (Aurora-style adaptation)
        health_endpoints = [
            base_url,  # Try the configured endpoint first
            base_url.replace("/healthz", "/health"),  # Try /health variant
            base_url.replace("/health", "/healthz"),  # Try /healthz variant
        ]
        
        for endpoint in health_endpoints:
            try:
                # Try GET request (more reliable than HEAD for varied APIs)
                result = subprocess.run(['curl', '-s', '-f', endpoint],
                                      capture_output=True, text=True, timeout=2)
                
                # Check if we got a response (any JSON or text response is good)
                if result.returncode == 0 and result.stdout:
                    # Look for positive health indicators
                    response = result.stdout.lower()
                    if any(indicator in response for indicator in ['ok', 'healthy', 'status', 'true']):
                        return True
            except:
                continue
        
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
