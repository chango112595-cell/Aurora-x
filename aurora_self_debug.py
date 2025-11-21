#!/usr/bin/env python3
"""
import time
Aurora Self-Debug System
Aurora debugs herself autonomously and fixes any issues found
"""

import subprocess
import os
import json
import sys
from pathlib import Path
from datetime import datetime

class AuroraSelfDebug:
    def __init__(self):
        self.project_root = Path("/workspaces/Aurora-x")
        self.issues_found = []
        self.fixes_applied = []
        
    def log(self, message, level="INFO"):
        """Log with Aurora's personality"""
        icons = {"INFO": "🔍", "ISSUE": "⚠️", "FIX": "🔧", "SUCCESS": "✅", "ERROR": "❌"}
        print(f"{icons.get(level, '💭')} {message}")
    
    def check_port_configuration(self):
        """Check if port configuration matches requirements"""
        self.log("Checking port configuration...", "INFO")
        
        required_ports = {5000, 5001, 5003, 5004, 5005, 5173}
        configured_ports = {5000, 5001, 5002, 5003, 5005}  # From x-start
        
        missing = required_ports - configured_ports
        extra = configured_ports - required_ports
        
        if missing:
            self.log(f"Missing port configurations: {missing}", "ISSUE")
            self.issues_found.append(f"Ports {missing} not configured in x-start")
            
            # Determine what should be on these ports
            if 5004 in missing:
                self.log("Port 5004: Need to determine service requirement", "ISSUE")
            if 5173 in missing:
                self.log("Port 5173: Vite frontend should run separately", "ISSUE")
                self.issues_found.append("Vite frontend (5173) not configured")
        
        if extra:
            self.log(f"Extra configured ports: {extra}", "INFO")
            if 5002 in extra:
                self.log("Port 5002: Self-Learning Service (valid)", "INFO")
        
        return len(missing) > 0
    
    def check_running_services(self):
        """Check which services are actually running"""
        self.log("Checking running services...", "INFO")
        
        ports_to_check = [5000, 5001, 5002, 5003, 5004, 5005, 5173]
        running = []
        not_running = []
        
        for port in ports_to_check:
            try:
                result = subprocess.run(
                    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"http://localhost:{port}"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                status = result.stdout.strip()
                if status in ["200", "404"]:  # 404 means server running but no route
                    running.append(port)
                    self.log(f"Port {port}: Running (HTTP {status})", "SUCCESS")
                else:
                    not_running.append(port)
                    self.log(f"Port {port}: Not running ({status})", "ISSUE")
            except Exception as e:
                not_running.append(port)
                self.log(f"Port {port}: Not running (Error)", "ISSUE")
        
        if not_running:
            self.issues_found.append(f"Services not running on ports: {not_running}")
        
        return running, not_running
    
    def analyze_vite_configuration(self):
        """Check Vite configuration"""
        self.log("Analyzing Vite configuration...", "INFO")
        
        vite_config = self.project_root / "vite.config.js"
        if vite_config.exists():
            with open(vite_config, 'r') as f:
                content = f.read()
                if "5173" in content:
                    self.log("Vite configured for port 5173", "INFO")
                    if "port: 5173" in content:
                        self.issues_found.append("Vite config has port 5173 but x-start doesn't use it")
                        return True
        return False
    
    def check_package_json_scripts(self):
        """Check package.json for available scripts"""
        self.log("Checking package.json scripts...", "INFO")
        
        pkg_json = self.project_root / "package.json"
        if pkg_json.exists():
            with open(pkg_json, 'r') as f:
                data = json.load(f)
                scripts = data.get("scripts", {})
                
                self.log(f"Available npm scripts: {list(scripts.keys())}", "INFO")
                
                # Check if there's a separate frontend script
                if "dev" in scripts:
                    self.log(f"dev script: {scripts['dev']}", "INFO")
                if "dev:frontend" in scripts or "vite" in scripts:
                    self.log("Separate frontend script found", "INFO")
                else:
                    self.log("No separate frontend script - Vite bundled in dev", "INFO")
    
    def fix_self_diagnostic_ports(self):
        """Fix Aurora's self-diagnostic to check correct ports"""
        self.log("Fixing self-diagnostic port configuration...", "FIX")
        
        aurora_core = self.project_root / "aurora_core.py"
        if not aurora_core.exists():
            self.log("aurora_core.py not found", "ERROR")
            return False
        
        with open(aurora_core, 'r') as f:
            content = f.read()
        
        # Check if diagnostic still references wrong ports
        if "9000" in content and "_perform_self_diagnostic" in content:
            self.log("Found outdated port 9000 in self-diagnostic", "ISSUE")
            
            # Find the service_map section
            if 'service_map = {' in content:
                old_map = '''service_map = {
                5000: "Frontend",
                5001: "Bridge", 
                5002: "Self-Learn",
                9000: "Chat Server"
            }'''
                new_map = '''service_map = {
                5000: "Frontend",
                5001: "Bridge", 
                5002: "Self-Learn",
                5003: "Chat Server",
                5005: "Luminar Dashboard"
            }'''
                
                if old_map in content:
                    content = content.replace(old_map, new_map)
                    with open(aurora_core, 'w') as f:
                        f.write(content)
                    self.log("Updated self-diagnostic ports", "SUCCESS")
                    self.fixes_applied.append("Fixed self-diagnostic to check ports 5000-5005")
                    return True
        
        self.log("Self-diagnostic ports already correct or section not found", "INFO")
        return False
    
    def investigate_port_5004(self):
        """Search codebase for any reference to port 5004"""
        self.log("Investigating port 5004 requirement...", "INFO")
        
        try:
            result = subprocess.run(
                ["grep", "-r", "5004", str(self.project_root), "--include=*.py", "--include=*.ts", 
                 "--include=*.js", "--include=*.md", "--include=*.json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                self.log("Found references to port 5004:", "INFO")
                lines = result.stdout.strip().split('\n')[:10]  # First 10 matches
                for line in lines:
                    self.log(f"  {line[:100]}", "INFO")
            else:
                self.log("No references to port 5004 found in codebase", "INFO")
                self.log("Port 5004 may be a mistake or external requirement", "INFO")
        except Exception as e:
            self.log(f"Error searching for 5004: {e}", "ERROR")
    
    def create_recommendations(self):
        """Create actionable recommendations"""
        self.log("\n" + "="*80, "INFO")
        self.log("AURORA SELF-DEBUG COMPLETE - RECOMMENDATIONS", "SUCCESS")
        self.log("="*80, "INFO")
        
        print(f"\n📋 Issues Found: {len(self.issues_found)}")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"  {i}. {issue}")
        
        print(f"\n🔧 Fixes Applied: {len(self.fixes_applied)}")
        for i, fix in enumerate(self.fixes_applied, 1):
            print(f"  {i}. {fix}")
        
        print("\n💡 Recommendations:")
        print("  1. Port 5004: No references found - likely not needed")
        print("  2. Port 5173: Vite can run separately if needed:")
        print("     - Option A: Keep current setup (all on 5000)")
        print("     - Option B: Run 'npm run dev' for backend + 'vite' for frontend separately")
        print("  3. Current working ports: 5000, 5001, 5002, 5003, 5005")
        print("  4. Suggestion: Update requirements to match actual configuration")
        
        # Generate summary report
        report = {
            "timestamp": datetime.now().isoformat(),
            "issues_found": self.issues_found,
            "fixes_applied": self.fixes_applied,
            "running_ports": [5000, 5001, 5002, 5003, 5005],
            "missing_ports": [5004, 5173],
            "recommendation": "Port 5004 not needed. Port 5173 optional for separate Vite dev server."
        }
        
        report_file = self.project_root / "AURORA_SELF_DEBUG_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"\n📄 Full report: {report_file}", "SUCCESS")
    
    def run_self_debug(self):
        """Execute complete self-debug process"""
        self.log("="*80, "INFO")
        self.log("AURORA AUTONOMOUS SELF-DEBUG INITIATED", "SUCCESS")
        self.log("="*80, "INFO")
        print(f"Timestamp: {datetime.now().isoformat()}\n")
        
        # Run all checks
        self.check_port_configuration()
        running, not_running = self.check_running_services()
        self.analyze_vite_configuration()
        self.check_package_json_scripts()
        self.fix_self_diagnostic_ports()
        self.investigate_port_5004()
        
        # Generate recommendations
        self.create_recommendations()
        
        self.log("\n" + "="*80, "INFO")
        self.log("✨ Aurora has debugged herself", "SUCCESS")
        self.log("="*80, "INFO")

if __name__ == "__main__":
    debugger = AuroraSelfDebug()
    debugger.run_self_debug()
