#!/usr/bin/env python3
"""
Luminar Nexus - Aurora's Server Command Center
Manages all development servers with proper process control
NOW MANAGED BY AURORA'S INTELLIGENCE SYSTEM
"""

import subprocess
import json
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Import Aurora's Intelligence Manager
sys.path.append(str(Path(__file__).parent.parent))
try:
    from aurora_intelligence_manager import AuroraIntelligenceManager
    AURORA_INTELLIGENCE = AuroraIntelligenceManager()
    AURORA_IS_BOSS = True
except ImportError:
    AURORA_INTELLIGENCE = None
    AURORA_IS_BOSS = False

class LuminarNexusServerManager:
    """
    Aurora's central server management system
    Uses tmux for persistent, manageable processes
    NOW SUBORDINATE TO AURORA'S INTELLIGENCE - SHE IS THE BOSS
    """
    
    def __init__(self):
        # Let Aurora know Luminar Nexus is starting up
        if AURORA_IS_BOSS:
            AURORA_INTELLIGENCE.log("🌟 Luminar Nexus initializing under Aurora's command")
        
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
    
    def _find_available_port(self, preferred_port: int, exclude_ports: set, start_range: int = 5000, end_range: int = 6000) -> int:
        """Find an available port, preferring the suggested port"""
        listening_ports = self._get_listening_ports()
        all_excluded = listening_ports | exclude_ports
        
        # Try preferred port first
        if preferred_port not in all_excluded:
            return preferred_port
        
        # Find next available port in range
        for port in range(start_range, end_range):
            if port not in all_excluded:
                print(f"   ⚠️  Port {preferred_port} in use, assigned {port} instead")
                return port
        
        raise Exception(f"No available ports in range {start_range}-{end_range}")
    
    def _auto_assign_ports(self):
        """
        Intelligently assign ports to all servers, avoiding conflicts
        Aurora makes the decisions, Luminar Nexus executes
        """
        if AURORA_IS_BOSS:
            AURORA_INTELLIGENCE.log("🎯 Aurora analyzing port allocation strategy...")
        
        print("🔍 Analyzing port availability...")
        
        listening_ports = self._get_listening_ports()
        assigned_ports = set()
        port_decisions = []
        
        for server_key, config in self.servers.items():
            preferred = config["preferred_port"]
            
            # Check if preferred port is available (not in use AND not already assigned)
            if preferred in listening_ports or preferred in assigned_ports:
                # Aurora decides on alternative port
                new_port = self._find_available_port(preferred, assigned_ports)
                config["port"] = new_port
                assigned_ports.add(new_port)
                
                decision = f"Port {preferred} conflict - reassigning {server_key} to {new_port}"
                port_decisions.append(decision)
                
                if AURORA_IS_BOSS:
                    AURORA_INTELLIGENCE.log(f"⚠️ {decision}")
                
                self.log_event("PORT_REASSIGNED", server_key, {
                    "preferred": preferred,
                    "assigned": new_port,
                    "reason": "port_conflict"
                })
            else:
                # Preferred port is available
                config["port"] = preferred
                assigned_ports.add(preferred)
                
                if AURORA_IS_BOSS:
                    AURORA_INTELLIGENCE.log(f"✅ {server_key} assigned to preferred port {preferred}")
        
        # Build health check URLs with assigned ports
        for config in self.servers.values():
            config["health_check"] = config["health_check_template"].format(port=config["port"])
            config["command"] = config["command_template"].format(port=config["port"])
        
        if AURORA_IS_BOSS and port_decisions:
            AURORA_INTELLIGENCE.log(f"📋 Aurora made {len(port_decisions)} port decisions")
        
        print(f"✅ Port assignment complete: {len(assigned_ports)} ports allocated")
        
        if AURORA_IS_BOSS:
            AURORA_INTELLIGENCE.log(f"🎯 Port allocation complete - all {len(self.servers)} servers configured")
    
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
    
    def start_autonomous_monitoring(self, check_interval=5):
        """
        Aurora's autonomous monitoring daemon - continuously monitors and self-heals
        This gives Aurora independent operation without external supervision
        Default: 5 second checks for fast response
        """
        print("\n" + "="*70)
        print("🤖 AURORA AUTONOMOUS MONITORING - ACTIVATED")
        print("="*70)
        print(f"Check interval: {check_interval} seconds (FAST MODE)")
        print("Aurora will now monitor and self-heal all servers autonomously")
        print("Press Ctrl+C to stop monitoring\n")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"\n🔍 [{timestamp}] Monitoring Cycle #{cycle_count}")
                print("-" * 70)
                
                failed_servers = []
                
                # Check all servers
                for server_key in self.servers.keys():
                    status = self.get_status(server_key)
                    server_name = status['server']
                    
                    if status['status'] == 'running':
                        print(f"  ✅ {server_name}: HEALTHY (port {status['port']})")
                    else:
                        print(f"  ❌ {server_name}: FAILED - {status['status']}")
                        failed_servers.append((server_key, server_name))
                
                # Auto-heal failed servers
                if failed_servers:
                    print(f"\n🔧 Aurora detected {len(failed_servers)} failed server(s) - initiating self-repair...")
                    
                    for server_key, server_name in failed_servers:
                        print(f"   🔄 Restarting {server_name}...")
                        self.stop_server(server_key)
                        time.sleep(2)
                        self.start_server(server_key)
                        time.sleep(3)
                        
                        # Verify fix
                        new_status = self.get_status(server_key)
                        if new_status['status'] == 'running':
                            print(f"   ✅ {server_name} RESTORED")
                        else:
                            print(f"   ⚠️ {server_name} still unstable - will retry next cycle")
                else:
                    print(f"  💚 All systems operational")
                
                print(f"\n⏱️  Next check in {check_interval} seconds...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Aurora autonomous monitoring stopped by user")
            print("All servers remain in their current state\n")

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
        print("  python luminar_nexus.py monitor          - Start autonomous monitoring daemon")
        print("\nAvailable servers: vite, backend, bridge, self-learn")
        return
    
    command = sys.argv[1]
    
    if command == "start-all":
        nexus.start_all()
    elif command == "stop-all":
        nexus.stop_all()
    elif command == "status":
        nexus.show_status()
    elif command == "monitor":
        # Aurora's autonomous mode
        nexus.start_autonomous_monitoring()
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
