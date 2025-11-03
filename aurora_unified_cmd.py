#!/usr/bin/env python3
"""
Aurora Unified Command Manager
- Single control point for ALL Aurora commands
- Callable from CLI, API, buttons, or scripts
- Eliminates command confusion and duplicate work
- All commands go through here - nothing runs directly
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading

class AuroraCommandManager:
    """Central command dispatcher for Aurora system"""
    
    def __init__(self):
        self.root = Path("/workspaces/Aurora-x")
        self.log_file = self.root / ".aurora_commands.log"
        self.running_processes = {}
        self.command_queue = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log command execution"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
    
    # ============ STARTUP COMMANDS ============
    
    def startup_full_system(self) -> Dict[str, Any]:
        """🚀 ONE COMMAND TO START EVERYTHING - fires up the whole system in correct order"""
        self.log("🚀 STARTING AURORA COMPLETE SYSTEM...")
        
        try:
            # Step 1: Kill any existing processes
            self.log("  1️⃣  Cleaning up old processes...")
            self.cleanup_system()
            
            # Step 2: Start Aurora services in correct order
            self.log("  2️⃣  Starting Bridge API (port 5001)...")
            self.start_service("bridge")
            time.sleep(2)
            
            self.log("  3️⃣  Starting Main Server (port 5000)...")
            self.start_service("main")
            time.sleep(2)
            
            self.log("  4️⃣  Starting Self-Learn Server (port 5002)...")
            self.start_service("self_learn")
            time.sleep(2)
            
            self.log("  5️⃣  Starting File Server (port 8080)...")
            self.start_service("file_server")
            time.sleep(2)
            
            # Step 3: Verify all services
            self.log("  6️⃣  Verifying all services...")
            health = self.check_system_health()
            
            if health["all_healthy"]:
                self.log("✅ ALL SYSTEMS ONLINE!", "SUCCESS")
                return {
                    "status": "running",
                    "message": "Aurora system fully operational",
                    "health": health,
                    "access_dashboard": "http://localhost:5000/"
                }
            else:
                self.log("⚠️  Some services not responding yet", "WARN")
                return {
                    "status": "partial",
                    "message": "Services starting, may need a moment...",
                    "health": health
                }
        except Exception as e:
            self.log(f"❌ Startup failed: {str(e)}", "ERROR")
            return {"status": "error", "message": str(e)}
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific Aurora service"""
        services = {
            "bridge": {
                "module": "aurora_x.bridge.service",
                "port": 5001,
                "name": "Bridge API"
            },
            "main": {
                "module": "aurora_x.serve",
                "port": 5000,
                "name": "Main Server"
            },
            "self_learn": {
                "module": "aurora_x.self_learn_server",
                "port": 5002,
                "name": "Self-Learn"
            },
            "file_server": {
                "cmd": ["python3", "-m", "http.server", "8080", "--bind", "0.0.0.0"],
                "cwd": str(self.root),
                "port": 8080,
                "name": "File Server"
            }
        }
        
        if service_name not in services:
            self.log(f"Unknown service: {service_name}", "ERROR")
            return False
        
        svc = services[service_name]
        
        try:
            # Kill any existing process on this port
            port = svc.get("port")
            if port:
                subprocess.run(
                    f"lsof -ti:{port} | xargs kill -9 2>/dev/null || true",
                    shell=True,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(0.5)
            
            if "module" in svc:
                cmd = [sys.executable, "-m", svc["module"]]
            else:
                cmd = svc["cmd"]
            
            process = subprocess.Popen(
                cmd,
                cwd=svc.get("cwd", str(self.root)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.running_processes[service_name] = process
            self.log(f"  ✅ {svc['name']} started on port {port}")
            return True
        except Exception as e:
            self.log(f"  ❌ Failed to start {svc['name']}: {str(e)}", "ERROR")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific Aurora service"""
        if service_name in self.running_processes:
            try:
                self.running_processes[service_name].terminate()
                del self.running_processes[service_name]
                self.log(f"✅ Stopped: {service_name}")
                return True
            except Exception as e:
                self.log(f"❌ Failed to stop {service_name}: {str(e)}", "ERROR")
                return False
        return False
    
    def cleanup_system(self) -> bool:
        """Kill all Aurora processes and clear ports"""
        try:
            for port in [5000, 5001, 5002, 8080]:
                subprocess.run(
                    f"lsof -ti:{port} | xargs kill -9 2>/dev/null || true",
                    shell=True,
                    stderr=subprocess.DEVNULL
                )
            self.log("✅ Cleanup complete")
            return True
        except Exception as e:
            self.log(f"⚠️  Cleanup warning: {str(e)}", "WARN")
            return True
    
    # ============ STATUS COMMANDS ============
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check if all Aurora services are healthy"""
        health_checks = {
            "main_server": ("http://localhost:5000/healthz", "Main Server"),
            "bridge_api": ("http://localhost:5001/healthz", "Bridge API"),
            "self_learn": ("http://localhost:5002/healthz", "Self-Learn"),
            "file_server": ("http://localhost:8080/", "File Server"),
        }
        
        results = {}
        
        for key, (url, name) in health_checks.items():
            try:
                result = subprocess.run(
                    ["curl", "-s", "-I", "--connect-timeout", "2", url],
                    capture_output=True,
                    timeout=3
                )
                results[key] = {
                    "name": name,
                    "status": "healthy" if result.returncode == 0 else "offline",
                    "url": url
                }
            except Exception:
                results[key] = {
                    "name": name,
                    "status": "offline",
                    "url": url
                }
        
        all_healthy = all(r["status"] == "healthy" for r in results.values())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "all_healthy": all_healthy,
            "services": results
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        health = self.check_system_health()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health": health,
            "processes": len(self.running_processes),
            "log_file": str(self.log_file)
        }
    
    # ============ TASK COMMANDS ============
    
    def run_aurora_auto_fix(self) -> Dict[str, Any]:
        """Have Aurora auto-fix herself"""
        self.log("🔧 Launching Aurora's self-healing system...")
        
        try:
            # Call Aurora's self-fix capabilities
            result = subprocess.run(
                [sys.executable, "-m", "aurora_x.auto_fix"],
                capture_output=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.log("✅ Aurora self-fix completed", "SUCCESS")
                return {
                    "status": "success",
                    "message": "Aurora analyzed and fixed issues",
                    "output": result.stdout.decode()
                }
            else:
                self.log("⚠️  Aurora self-fix completed with warnings", "WARN")
                return {
                    "status": "warning",
                    "message": "Self-fix ran but found issues",
                    "output": result.stderr.decode()
                }
        except Exception as e:
            self.log(f"❌ Self-fix failed: {str(e)}", "ERROR")
            return {"status": "error", "message": str(e)}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all Aurora tests"""
        self.log("🧪 Running Aurora test suite...")
        
        try:
            result = subprocess.run(
                ["make", "test"],
                cwd=str(self.root),
                capture_output=True,
                timeout=300
            )
            
            success = result.returncode == 0
            self.log(f"{'✅' if success else '❌'} Tests {'passed' if success else 'failed'}")
            
            return {
                "status": "passed" if success else "failed",
                "output": result.stdout.decode()[-500:]  # Last 500 chars
            }
        except Exception as e:
            self.log(f"❌ Tests error: {str(e)}", "ERROR")
            return {"status": "error", "message": str(e)}
    
    def view_logs(self, lines: int = 50) -> str:
        """View Aurora command logs"""
        try:
            result = subprocess.run(
                ["tail", "-n", str(lines), str(self.log_file)],
                capture_output=True
            )
            return result.stdout.decode()
        except:
            return "No logs yet"
    
    # ============ CLI INTERFACE ============
    
    def parse_command(self, cmd: str, args: List[str] = None) -> Dict[str, Any]:
        """Parse and execute commands"""
        commands = {
            "start": self.startup_full_system,
            "status": self.get_system_status,
            "health": self.check_system_health,
            "stop": lambda: self.cleanup_system(),
            "fix": self.run_aurora_auto_fix,
            "test": self.run_all_tests,
            "logs": lambda: self.view_logs(100),
        }
        
        if cmd in commands:
            return commands[cmd]()
        else:
            return {"error": f"Unknown command: {cmd}"}


def main():
    """CLI interface"""
    manager = AuroraCommandManager()
    
    if len(sys.argv) < 2:
        print("🌌 Aurora Unified Command Manager")
        print("\nUsage: aurora-cmd <command> [options]")
        print("\nCommands:")
        print("  start           Start the complete Aurora system")
        print("  status          Show current system status")
        print("  health          Check service health")
        print("  stop            Stop all Aurora services")
        print("  fix             Run Aurora's self-healing")
        print("  test            Run all tests")
        print("  logs            View command logs")
        return
    
    cmd = sys.argv[1]
    result = manager.parse_command(cmd, sys.argv[2:])
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
