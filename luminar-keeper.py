#!/usr/bin/env python3
"""
Luminar Keeper - Auto-Manages Aurora's Servers
Ensures servers stay running and auto-restarts if they crash
"""

import subprocess
import time
import sys
import json
from datetime import datetime
from pathlib import Path
import os
import signal

PROJECT_ROOT = "/workspaces/Aurora-x"
LUMINAR_SCRIPT = f"{PROJECT_ROOT}/tools/luminar_nexus.py"
KEEPER_PID_FILE = "/tmp/luminar_keeper.pid"
KEEPER_LOG = "/tmp/luminar_keeper.log"

class LuminarKeeper:
    def __init__(self):
        self.running = True
        self.restart_count = 0
        self.last_restart = time.time()
        
        # Ensure log file exists
        Path(KEEPER_LOG).touch()
    
    def log(self, level, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        colors = {
            "INFO": "\033[0;34m",    # Blue
            "SUCCESS": "\033[0;32m", # Green
            "WARN": "\033[1;33m",    # Yellow
            "ERROR": "\033[0;31m",   # Red
        }
        color = colors.get(level, "")
        reset = "\033[0m"
        
        log_entry = f"[{level}] {timestamp} {message}"
        print(f"{color}{log_entry}{reset}")
        
        with open(KEEPER_LOG, "a") as f:
            f.write(log_entry + "\n")
    
    def check_health(self):
        """Check if servers are responding"""
        try:
            # Check backend
            result_backend = subprocess.run(
                ["curl", "-s", "-I", "http://localhost:5000"],
                capture_output=True, text=True, timeout=2
            )
            backend_ok = result_backend.returncode == 0
            
            # Check frontend
            result_vite = subprocess.run(
                ["curl", "-s", "-I", "http://localhost:5001"],
                capture_output=True, text=True, timeout=2
            )
            vite_ok = result_vite.returncode == 0
            
            return backend_ok and vite_ok
        except Exception as e:
            return False
    
    def start_servers(self):
        """Start all Aurora servers using start-dev.sh"""
        self.log("INFO", "Starting Aurora servers...")
        
        try:
            # Use start-dev.sh which is proven to work
            result = subprocess.run(
                [f"{PROJECT_ROOT}/start-dev.sh", "start"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log("SUCCESS", "Aurora servers started successfully")
                return True
            else:
                self.log("ERROR", f"Failed to start: {result.stderr}")
                return False
        except Exception as e:
            self.log("ERROR", f"Exception starting servers: {e}")
            return False
    
    def get_status(self):
        """Get current server status"""
        try:
            result = subprocess.run(
                [sys.executable, LUMINAR_SCRIPT, "status"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout
        except:
            return "Unable to get status"
    
    def signal_handler(self, sig, frame):
        """Handle shutdown signals"""
        self.log("WARN", "Shutting down Luminar Keeper...")
        self.running = False
    
    def run(self):
        """Main keeper loop"""
        self.log("SUCCESS", f"🌟 Luminar Keeper started (PID: {os.getpid()})")
        self.log("INFO", "Watching Aurora servers every 30 seconds...")
        
        # Save keeper PID
        with open(KEEPER_PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Initial start
        self.start_servers()
        time.sleep(5)
        
        # Main loop
        cycle = 0
        while self.running:
            cycle += 1
            
            if self.check_health():
                # Servers healthy
                if self.restart_count > 0:
                    self.log("SUCCESS", f"✅ Servers recovered! Cycle #{cycle}")
                    self.restart_count = 0
                else:
                    # Log every 10 cycles (5 minutes)
                    if cycle % 10 == 0:
                        self.log("INFO", f"✅ Health OK (cycle #{cycle})")
            else:
                # Servers unhealthy
                self.restart_count += 1
                self.log("WARN", f"⚠️  Health check FAILED (attempt #{self.restart_count})")
                
                # Log full status
                status = self.get_status()
                for line in status.split("\n"):
                    if line.strip():
                        self.log("INFO", f"  {line}")
                
                # Restart servers
                if self.start_servers():
                    time.sleep(5)
                    if self.check_health():
                        self.log("SUCCESS", f"✅ Restart successful!")
                        self.restart_count = 0
                    else:
                        self.log("ERROR", "❌ Restart failed - servers not responding")
                else:
                    self.log("ERROR", "❌ Failed to restart servers")
            
            # Sleep before next check
            try:
                time.sleep(30)
            except KeyboardInterrupt:
                break
        
        self.log("SUCCESS", "🛑 Luminar Keeper stopped")


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Luminar Keeper - Aurora Server Auto-Manager")
        print()
        print("Usage: luminar-keeper.py [COMMAND]")
        print()
        print("Commands:")
        print("  start      Start Keeper daemon (watches servers)")
        print("  stop       Stop Keeper daemon")
        print("  status     Show Keeper and server status")
        print("  logs       Tail Keeper logs")
        print()
        return
    
    command = sys.argv[1]
    
    if command == "start":
        # Start in background
        keeper = LuminarKeeper()
        keeper.run()
    
    elif command == "stop":
        # Stop keeper and servers
        if Path(KEEPER_PID_FILE).exists():
            pid = int(Path(KEEPER_PID_FILE).read_text().strip())
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"✅ Stopped Luminar Keeper (PID: {pid})")
            except:
                print(f"⚠️  Could not kill PID {pid}")
        
        # Also stop Luminar servers
        subprocess.run([f"{PROJECT_ROOT}/start-dev.sh", "stop"], 
                      cwd=PROJECT_ROOT, capture_output=True)
        print("✅ Aurora servers stopped")
    
    elif command == "status":
        # Show status
        if Path(KEEPER_PID_FILE).exists():
            pid = int(Path(KEEPER_PID_FILE).read_text().strip())
            try:
                os.kill(pid, 0)  # Check if process exists
                print(f"✅ Keeper: RUNNING (PID: {pid})")
            except:
                print(f"❌ Keeper: STOPPED (stale PID: {pid})")
        else:
            print("❌ Keeper: NOT RUNNING")
        
        print()
        result = subprocess.run([sys.executable, LUMINAR_SCRIPT, "status"],
                              cwd=PROJECT_ROOT, capture_output=True, text=True)
        print(result.stdout)
    
    elif command == "logs":
        # Tail logs
        os.execvp("tail", ["tail", "-f", KEEPER_LOG])
    
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
