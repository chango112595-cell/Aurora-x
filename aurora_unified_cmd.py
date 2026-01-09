#!/usr/bin/env python3
"""
Aurora Unified Command Manager
Provides unified command interface for Aurora-X system control
"""

import json
import logging
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup logging
log_dir = Path(".aurora_logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "command_manager.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class AuroraCommandManager:
    """Unified command manager for Aurora-X system"""
    
    def __init__(self):
        self.logs: List[str] = []
        self.services = {
            "backend": {"port": 5000, "cmd": ["npm", "run", "dev"]},
            "nexus_v3": {"port": 5002, "cmd": ["python3", "aurora_nexus_v3/main.py"]},
            "luminar": {"port": 8000, "cmd": ["python3", "tools/luminar_nexus_v2.py", "serve"]},
            "memory": {"port": 5003, "cmd": ["python3", "server/memory-bridge.py"]},
            "memory_fabric": {"port": 5004, "cmd": ["python3", "aurora_memory_fabric_v2/service.py"]},
        }
        self.processes: Dict[str, subprocess.Popen] = {}
        self._log("AuroraCommandManager initialized")
    
    def _log(self, message: str):
        """Internal logging"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        logger.info(message)
        # Keep only last 1000 log entries
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]
    
    def _check_port(self, port: int, timeout: float = 1.0) -> bool:
        """Check if a port is accepting connections"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def startup_full_system(self) -> Dict[str, Any]:
        """Start all Aurora services"""
        self._log("Starting full Aurora system...")
        results = {}
        
        for service_name, config in self.services.items():
            try:
                if service_name in self.processes:
                    self._log(f"{service_name} already running")
                    results[service_name] = {"status": "already_running"}
                    continue
                
                self._log(f"Starting {service_name}...")
                proc = subprocess.Popen(
                    config["cmd"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=Path.cwd()
                )
                self.processes[service_name] = proc
                
                # Wait a bit and check if it's still running
                time.sleep(2)
                if proc.poll() is None:
                    results[service_name] = {"status": "started", "pid": proc.pid}
                    self._log(f"{service_name} started (PID: {proc.pid})")
                else:
                    stdout, stderr = proc.communicate()
                    results[service_name] = {
                        "status": "failed",
                        "error": stderr.decode() if stderr else "Unknown error"
                    }
                    self._log(f"{service_name} failed to start")
            except Exception as e:
                results[service_name] = {"status": "error", "error": str(e)}
                self._log(f"Error starting {service_name}: {e}")
        
        return {
            "success": True,
            "message": "System startup initiated",
            "services": results
        }
    
    def cleanup_system(self) -> bool:
        """Stop all Aurora services"""
        self._log("Cleaning up Aurora system...")
        success = True
        
        for service_name, proc in list(self.processes.items()):
            try:
                self._log(f"Stopping {service_name}...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                self._log(f"{service_name} stopped")
            except Exception as e:
                self._log(f"Error stopping {service_name}: {e}")
                success = False
        
        self.processes.clear()
        return success
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "timestamp": time.time(),
            "services": {},
            "ports": {},
            "processes": len(self.processes)
        }
        
        for service_name, config in self.services.items():
            port = config["port"]
            is_running = self._check_port(port)
            proc_running = service_name in self.processes and self.processes[service_name].poll() is None
            
            status["services"][service_name] = {
                "running": is_running or proc_running,
                "port": port,
                "process": "running" if proc_running else "stopped"
            }
            status["ports"][port] = is_running
        
        return status
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check system health"""
        status = self.get_system_status()
        healthy_services = sum(1 for s in status["services"].values() if s["running"])
        total_services = len(status["services"])
        
        return {
            "healthy": healthy_services == total_services,
            "services_healthy": healthy_services,
            "services_total": total_services,
            "status": status,
            "timestamp": time.time()
        }
    
    def run_aurora_auto_fix(self) -> Dict[str, Any]:
        """Run Aurora's auto-fix system"""
        self._log("Running Aurora auto-fix...")
        
        try:
            # Try to import and run auto-fix if available
            sys.path.insert(0, str(Path.cwd()))
            
            # Check for self-healing tools
            fix_scripts = [
                "tools/aurora_self_heal.py",
                "tools/aurora_self_repair.py",
                "tools/aurora_self_diagnostic.py"
            ]
            
            results = []
            for script in fix_scripts:
                script_path = Path(script)
                if script_path.exists():
                    try:
                        self._log(f"Running {script}...")
                        result = subprocess.run(
                            [sys.executable, str(script_path)],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        results.append({
                            "script": script,
                            "success": result.returncode == 0,
                            "output": result.stdout[:500] if result.stdout else ""
                        })
                    except Exception as e:
                        results.append({
                            "script": script,
                            "success": False,
                            "error": str(e)
                        })
            
            return {
                "success": True,
                "message": "Auto-fix completed",
                "results": results
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        self._log("Running all tests...")
        
        test_commands = [
            ["python3", "-m", "pytest", "tests/", "-v"],
            ["npm", "test", "--", "--passWithNoTests"]
        ]
        
        results = []
        for cmd in test_commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=Path.cwd()
                )
                results.append({
                    "command": " ".join(cmd),
                    "success": result.returncode == 0,
                    "output": result.stdout[:1000] if result.stdout else result.stderr[:1000]
                })
            except Exception as e:
                results.append({
                    "command": " ".join(cmd),
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "results": results
        }
    
    def view_logs(self, lines: int = 50) -> List[str]:
        """View recent logs"""
        return self.logs[-lines:] if lines > 0 else self.logs
    
    def parse_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """Parse and execute a command"""
        args = args or []
        command_lower = command.lower().strip()
        
        self._log(f"Parsing command: {command}")
        
        if command_lower in ["start", "startup", "start all"]:
            return self.startup_full_system()
        elif command_lower in ["stop", "shutdown", "stop all"]:
            return {"success": self.cleanup_system(), "message": "System stopped"}
        elif command_lower in ["status", "health"]:
            return self.get_system_status()
        elif command_lower in ["fix", "auto-fix", "heal"]:
            return self.run_aurora_auto_fix()
        elif command_lower in ["test", "tests"]:
            return self.run_all_tests()
        elif command_lower in ["logs", "log"]:
            return {"logs": self.view_logs(int(args[0]) if args else 50)}
        else:
            return {
                "success": False,
                "error": f"Unknown command: {command}",
                "available_commands": [
                    "start", "stop", "status", "fix", "test", "logs"
                ]
            }


# Singleton instance
_manager_instance: Optional[AuroraCommandManager] = None


def get_manager() -> AuroraCommandManager:
    """Get singleton command manager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = AuroraCommandManager()
    return _manager_instance


# For backward compatibility
AuroraCommandManager = AuroraCommandManager
