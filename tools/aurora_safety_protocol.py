#!/usr/bin/env python3
"""
Aurora Safety Protocol System
Provides continuous auto-save, crash recovery, diagnostics, and never-lose-work guarantees
"""

import json
import time
import threading
import os
import sys
import datetime
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import subprocess
import signal

# Configuration
SAFETY_DIR = Path("/workspaces/Aurora-x/safety_data")
STATE_FILE = SAFETY_DIR / "aurora_state.json"
CRASH_LOG = SAFETY_DIR / "crash_recovery.json"
DIAGNOSTIC_LOG = SAFETY_DIR / "diagnostics.json"
SESSION_LOG = SAFETY_DIR / "session_history.json"
AUTO_SAVE_INTERVAL = 30  # seconds


@dataclass
class SystemState:
    """Complete system state snapshot"""
    timestamp: str
    services: Dict[str, Any]
    code_checksum: str
    config_files: Dict[str, str]
    session_data: Dict[str, Any]
    environment_vars: Dict[str, str]
    active_processes: List[Dict[str, Any]]
    diagnostics_summary: Dict[str, Any]


@dataclass
class DiagnosticReport:
    """Diagnostic check report"""
    timestamp: str
    check_name: str
    status: str  # "PASS", "WARN", "FAIL"
    details: str
    recommendations: List[str]
    auto_fixable: bool


@dataclass
class CrashEvent:
    """Crash event record"""
    timestamp: str
    service_name: str
    exit_code: int
    error_message: str
    stack_trace: str
    state_snapshot: Optional[SystemState]
    recovery_attempted: bool
    recovery_successful: bool


class AuroraSafetyProtocol:
    """Main safety protocol manager"""
    
    def __init__(self):
        self.running = False
        self.auto_save_thread: Optional[threading.Thread] = None
        self.last_save_time = 0
        self.crash_events: List[CrashEvent] = []
        self.diagnostic_reports: List[DiagnosticReport] = []
        
        # Ensure safety directory exists
        SAFETY_DIR.mkdir(exist_ok=True)
        
        # Load previous state if exists
        self.load_previous_state()
    
    def load_previous_state(self):
        """Load previous state for crash recovery"""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    print(f"✅ Loaded previous state from {data.get('timestamp', 'unknown time')}")
                    return data
            else:
                print("ℹ️  No previous state found (first run)")
                return None
        except Exception as e:
            print(f"⚠️  Failed to load previous state: {e}")
            return None
    
    def capture_system_state(self) -> SystemState:
        """Capture complete system state snapshot"""
        import hashlib
        import psutil
        
        # Calculate code checksum for critical files
        code_files = [
            "/workspaces/Aurora-x/tools/aurora_supervisor.py",
            "/workspaces/Aurora-x/tools/aurora_health_dashboard.py",
            "/workspaces/Aurora-x/tools/aurora_safety_protocol.py",
        ]
        
        code_checksum = hashlib.md5()
        for file_path in code_files:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    code_checksum.update(f.read())
        
        # Capture config files
        config_files = {}
        config_paths = [
            "/workspaces/Aurora-x/tools/aurora_supervisor_config.json",
            "/workspaces/Aurora-x/aurora_server_config.json",
        ]
        for config_path in config_paths:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_files[config_path] = f.read()
        
        # Get service status from health monitor
        services = self._get_services_status()
        
        # Capture active processes
        active_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                if any(keyword in ' '.join(proc.info['cmdline'] or []) 
                       for keyword in ['aurora', 'uvicorn', 'vite', 'python']):
                    active_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Environment variables (filtered for security)
        safe_env_vars = {k: v for k, v in os.environ.items() 
                        if not any(secret in k.lower() for secret in ['key', 'token', 'password', 'secret'])}
        
        return SystemState(
            timestamp=datetime.datetime.now().isoformat(),
            services=services,
            code_checksum=code_checksum.hexdigest(),
            config_files=config_files,
            session_data=self._capture_session_data(),
            environment_vars=safe_env_vars,
            active_processes=active_processes,
            diagnostics_summary=self._get_diagnostics_summary()
        )
    
    def _get_services_status(self) -> Dict[str, Any]:
        """Get current service status from health monitor"""
        try:
            import requests
            response = requests.get('http://localhost:9090/api/status', timeout=2)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return {"services": {}, "timestamp": datetime.datetime.now().isoformat()}
    
    def _capture_session_data(self) -> Dict[str, Any]:
        """Capture current session data"""
        return {
            "start_time": datetime.datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.last_save_time if self.last_save_time else 0,
            "auto_saves_count": getattr(self, 'save_count', 0),
            "crashes_detected": len(self.crash_events),
            "diagnostics_run": len(self.diagnostic_reports)
        }
    
    def _get_diagnostics_summary(self) -> Dict[str, Any]:
        """Get summary of recent diagnostics"""
        if not self.diagnostic_reports:
            return {"status": "No diagnostics run yet", "health_score": 100}
        
        recent = self.diagnostic_reports[-10:]  # Last 10 diagnostics
        passed = sum(1 for r in recent if r.status == "PASS")
        warned = sum(1 for r in recent if r.status == "WARN")
        failed = sum(1 for r in recent if r.status == "FAIL")
        
        health_score = (passed * 100 + warned * 50) / len(recent)
        
        return {
            "total_checks": len(recent),
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "health_score": round(health_score, 2),
            "last_check": recent[-1].timestamp if recent else None
        }
    
    def save_state(self, reason: str = "auto-save"):
        """Save current system state"""
        try:
            state = self.capture_system_state()
            
            # Save to file
            with open(STATE_FILE, 'w') as f:
                json.dump({
                    "reason": reason,
                    "state": asdict(state)
                }, f, indent=2)
            
            self.last_save_time = time.time()
            self.save_count = getattr(self, 'save_count', 0) + 1
            
            print(f"💾 State saved ({reason}) - Save #{self.save_count}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save state: {e}")
            traceback.print_exc()
            return False
    
    def auto_save_loop(self):
        """Continuous auto-save every 30 seconds"""
        print(f"🔄 Auto-save enabled (every {AUTO_SAVE_INTERVAL}s)")
        
        while self.running:
            time.sleep(AUTO_SAVE_INTERVAL)
            if self.running:  # Check again in case stopped during sleep
                self.save_state(reason="auto-save")
    
    def start_auto_save(self):
        """Start continuous auto-save"""
        if self.auto_save_thread and self.auto_save_thread.is_alive():
            print("⚠️  Auto-save already running")
            return
        
        self.running = True
        self.auto_save_thread = threading.Thread(target=self.auto_save_loop, daemon=True)
        self.auto_save_thread.start()
        print("✅ Auto-save started")
    
    def stop_auto_save(self):
        """Stop auto-save (triggers final save)"""
        if self.running:
            print("🛑 Stopping auto-save...")
            self.running = False
            
            # Wait for thread to finish
            if self.auto_save_thread:
                self.auto_save_thread.join(timeout=5)
            
            # Final save
            self.save_state(reason="shutdown")
            print("✅ Auto-save stopped, final state saved")
    
    def run_diagnostics(self) -> List[DiagnosticReport]:
        """Run comprehensive system diagnostics"""
        print("🔍 Running system diagnostics...")
        reports = []
        
        # Check 1: Service Health
        services_report = self._check_services_health()
        reports.append(services_report)
        
        # Check 2: Port Availability
        ports_report = self._check_port_availability()
        reports.append(ports_report)
        
        # Check 3: Process Health
        process_report = self._check_process_health()
        reports.append(process_report)
        
        # Check 4: File System
        filesystem_report = self._check_filesystem()
        reports.append(filesystem_report)
        
        # Check 5: Configuration Integrity
        config_report = self._check_config_integrity()
        reports.append(config_report)
        
        # Store reports
        self.diagnostic_reports.extend(reports)
        self._save_diagnostic_reports()
        
        # Print summary
        print("\n📊 Diagnostic Summary:")
        for report in reports:
            icon = "✅" if report.status == "PASS" else "⚠️" if report.status == "WARN" else "❌"
            print(f"{icon} {report.check_name}: {report.status}")
            if report.details:
                print(f"   Details: {report.details}")
        
        return reports
    
    def _check_services_health(self) -> DiagnosticReport:
        """Check if all services are healthy"""
        try:
            status = self._get_services_status()
            services = status.get('services', {})
            
            if not services:
                return DiagnosticReport(
                    timestamp=datetime.datetime.now().isoformat(),
                    check_name="Service Health",
                    status="FAIL",
                    details="Cannot connect to health monitor",
                    recommendations=["Check if aurora_supervisor.py is running", "Verify health dashboard on port 9090"],
                    auto_fixable=True
                )
            
            running = sum(1 for s in services.values() if s.get('status') == 'running')
            total = len(services)
            
            if running == total:
                status_result = "PASS"
                details = f"All {total} services running"
            elif running > 0:
                status_result = "WARN"
                details = f"{running}/{total} services running"
            else:
                status_result = "FAIL"
                details = "No services running"
            
            return DiagnosticReport(
                timestamp=datetime.datetime.now().isoformat(),
                check_name="Service Health",
                status=status_result,
                details=details,
                recommendations=["Start stopped services via health dashboard"] if running < total else [],
                auto_fixable=True
            )
            
        except Exception as e:
            return DiagnosticReport(
                timestamp=datetime.datetime.now().isoformat(),
                check_name="Service Health",
                status="FAIL",
                details=f"Error checking services: {str(e)}",
                recommendations=["Check supervisor logs", "Restart aurora_supervisor.py"],
                auto_fixable=False
            )
    
    def _check_port_availability(self) -> DiagnosticReport:
        """Check if required ports are available"""
        import socket
        
        required_ports = [5000, 5001, 5002, 8080, 9090]
        conflicts = []
        
        for port in required_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result != 0:  # Port not in use (should be in use by our services)
                conflicts.append(f"Port {port} not listening")
        
        if not conflicts:
            return DiagnosticReport(
                timestamp=datetime.datetime.now().isoformat(),
                check_name="Port Availability",
                status="PASS",
                details="All required ports listening",
                recommendations=[],
                auto_fixable=False
            )
        else:
            return DiagnosticReport(
                timestamp=datetime.datetime.now().isoformat(),
                check_name="Port Availability",
                status="WARN",
                details=", ".join(conflicts),
                recommendations=["Start missing services"],
                auto_fixable=True
            )
    
    def _check_process_health(self) -> DiagnosticReport:
        """Check if critical processes are running"""
        import psutil
        
        required_processes = ['aurora_supervisor', 'uvicorn', 'vite']
        found = []
        
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                for req in required_processes:
                    if req in cmdline and req not in found:
                        found.append(req)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        missing = set(required_processes) - set(found)
        
        if not missing:
            return DiagnosticReport(
                timestamp=datetime.datetime.now().isoformat(),
                check_name="Process Health",
                status="PASS",
                details=f"All {len(required_processes)} critical processes running",
                recommendations=[],
                auto_fixable=False
            )
        else:
            return DiagnosticReport(
                timestamp=datetime.datetime.now().isoformat(),
                check_name="Process Health",
                status="WARN",
                details=f"Missing: {', '.join(missing)}",
                recommendations=[f"Start {p}" for p in missing],
                auto_fixable=True
            )
    
    def _check_filesystem(self) -> DiagnosticReport:
        """Check filesystem health"""
        import shutil
        
        disk = shutil.disk_usage("/workspaces/Aurora-x")
        percent_used = (disk.used / disk.total) * 100
        
        if percent_used < 80:
            status_result = "PASS"
            details = f"Disk usage: {percent_used:.1f}%"
            recommendations = []
        elif percent_used < 90:
            status_result = "WARN"
            details = f"Disk usage: {percent_used:.1f}% (getting high)"
            recommendations = ["Consider cleaning up old logs and temp files"]
        else:
            status_result = "FAIL"
            details = f"Disk usage: {percent_used:.1f}% (critical)"
            recommendations = ["Clean up disk space immediately", "Remove old backups"]
        
        return DiagnosticReport(
            timestamp=datetime.datetime.now().isoformat(),
            check_name="Filesystem Health",
            status=status_result,
            details=details,
            recommendations=recommendations,
            auto_fixable=False
        )
    
    def _check_config_integrity(self) -> DiagnosticReport:
        """Check configuration file integrity"""
        config_files = [
            "/workspaces/Aurora-x/tools/aurora_supervisor_config.json",
            "/workspaces/Aurora-x/aurora_server_config.json",
        ]
        
        issues = []
        for config_path in config_files:
            if not os.path.exists(config_path):
                issues.append(f"Missing: {os.path.basename(config_path)}")
            else:
                try:
                    with open(config_path, 'r') as f:
                        json.load(f)  # Validate JSON
                except json.JSONDecodeError as e:
                    issues.append(f"Invalid JSON in {os.path.basename(config_path)}: {e}")
        
        if not issues:
            return DiagnosticReport(
                timestamp=datetime.datetime.now().isoformat(),
                check_name="Configuration Integrity",
                status="PASS",
                details="All config files valid",
                recommendations=[],
                auto_fixable=False
            )
        else:
            return DiagnosticReport(
                timestamp=datetime.datetime.now().isoformat(),
                check_name="Configuration Integrity",
                status="FAIL",
                details=", ".join(issues),
                recommendations=["Restore config files from backup", "Regenerate missing configs"],
                auto_fixable=True
            )
    
    def _save_diagnostic_reports(self):
        """Save diagnostic reports to file"""
        try:
            with open(DIAGNOSTIC_LOG, 'w') as f:
                json.dump([asdict(r) for r in self.diagnostic_reports], f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save diagnostic reports: {e}")
    
    def record_crash(self, service_name: str, exit_code: int, error_message: str, 
                    stack_trace: str = ""):
        """Record a service crash event"""
        print(f"💥 Recording crash event for {service_name}")
        
        crash = CrashEvent(
            timestamp=datetime.datetime.now().isoformat(),
            service_name=service_name,
            exit_code=exit_code,
            error_message=error_message,
            stack_trace=stack_trace,
            state_snapshot=self.capture_system_state(),
            recovery_attempted=False,
            recovery_successful=False
        )
        
        self.crash_events.append(crash)
        
        # Save crash log
        try:
            with open(CRASH_LOG, 'w') as f:
                json.dump([asdict(c) for c in self.crash_events], f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save crash log: {e}")
        
        return crash
    
    def attempt_crash_recovery(self, crash: CrashEvent) -> bool:
        """Attempt to recover from a crash"""
        print(f"🔧 Attempting crash recovery for {crash.service_name}...")
        
        crash.recovery_attempted = True
        
        # Try to restart the service
        try:
            import requests
            response = requests.post('http://localhost:9090/api/control', 
                                   json={"service": crash.service_name, "action": "start"},
                                   timeout=5)
            
            if response.status_code == 200:
                print(f"✅ Successfully restarted {crash.service_name}")
                crash.recovery_successful = True
                return True
            else:
                print(f"❌ Failed to restart {crash.service_name}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Recovery failed: {e}")
            crash.recovery_successful = False
            return False
    
    def graceful_shutdown(self):
        """Perform graceful shutdown with all safety checks"""
        print("\n🛑 Initiating graceful shutdown...")
        print("=" * 60)
        
        # Step 1: Save everything
        print("\n1️⃣  Saving all state...")
        self.save_state(reason="graceful-shutdown")
        
        # Step 2: Run diagnostics
        print("\n2️⃣  Running final diagnostics...")
        reports = self.run_diagnostics()
        
        # Step 3: Stop auto-save
        print("\n3️⃣  Stopping auto-save...")
        self.stop_auto_save()
        
        # Step 4: Create shutdown report
        print("\n4️⃣  Creating shutdown report...")
        shutdown_report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "graceful_shutdown",
            "diagnostics": [asdict(r) for r in reports],
            "crashes_during_session": len(self.crash_events),
            "final_state": asdict(self.capture_system_state())
        }
        
        with open(SAFETY_DIR / "last_shutdown.json", 'w') as f:
            json.dump(shutdown_report, f, indent=2)
        
        print("\n✅ Graceful shutdown complete")
        print("=" * 60)
    
    def emergency_shutdown(self):
        """Emergency shutdown (save what we can)"""
        print("\n🚨 EMERGENCY SHUTDOWN")
        try:
            self.save_state(reason="emergency-shutdown")
            self.stop_auto_save()
            print("✅ Emergency state saved")
        except Exception as e:
            print(f"❌ Emergency save failed: {e}")
    
    def get_luminar_nexus_data(self) -> Dict[str, Any]:
        """Get formatted data for Luminar Nexus dashboard"""
        state = self.capture_system_state()
        
        return {
            "operational_health": {
                "score": state.diagnostics_summary.get('health_score', 0),
                "status": "Healthy" if state.diagnostics_summary.get('health_score', 0) > 80 else "Degraded",
                "checks_passed": state.diagnostics_summary.get('passed', 0),
                "checks_warned": state.diagnostics_summary.get('warned', 0),
                "checks_failed": state.diagnostics_summary.get('failed', 0),
            },
            "session_info": state.session_data,
            "service_status": state.services,
            "recent_diagnostics": [asdict(r) for r in self.diagnostic_reports[-20:]],
            "crash_history": [asdict(c) for c in self.crash_events[-10:]],
            "auto_save_active": self.running,
            "last_save": self.last_save_time,
            "total_saves": getattr(self, 'save_count', 0)
        }


# CLI Interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora Safety Protocol System")
    parser.add_argument('--start', action='store_true', help='Start auto-save daemon')
    parser.add_argument('--stop', action='store_true', help='Stop auto-save daemon')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--diagnose', action='store_true', help='Run diagnostics')
    parser.add_argument('--save', action='store_true', help='Save state now')
    parser.add_argument('--luminar', action='store_true', help='Output Luminar Nexus data')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon (blocks)')
    
    args = parser.parse_args()
    
    protocol = AuroraSafetyProtocol()
    
    if args.start or args.daemon:
        protocol.start_auto_save()
        if args.daemon:
            print("Running in daemon mode (Ctrl+C to stop)...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                protocol.graceful_shutdown()
    
    if args.stop:
        protocol.stop_auto_save()
    
    if args.diagnose:
        protocol.run_diagnostics()
    
    if args.save:
        protocol.save_state(reason="manual")
    
    if args.status:
        state = protocol.capture_system_state()
        print(json.dumps(asdict(state), indent=2))
    
    if args.luminar:
        data = protocol.get_luminar_nexus_data()
        print(json.dumps(data, indent=2))
    
    if not any(vars(args).values()):
        parser.print_help()


if __name__ == "__main__":
    main()
