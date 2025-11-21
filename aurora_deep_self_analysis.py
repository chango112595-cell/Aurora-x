#!/usr/bin/env python3
"""
import time
Aurora Deep Self-Analysis System
Comprehensive introspection of Aurora's entire architecture, code, and operational state
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import psutil
import traceback

class AuroraDeepAnalysis:
    def __init__(self):
        self.project_root = Path("/workspaces/Aurora-x")
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "system_health": {},
            "services": {},
            "code_quality": {},
            "architecture": {},
            "performance": {},
            "issues": [],
            "recommendations": []
        }
    
    def analyze_services(self):
        """Check all Aurora services and their status"""
        print("\n" + "="*80)
        print("🔍 ANALYZING SERVICES")
        print("="*80)
        
        services = {
            5000: "Frontend Server",
            5001: "Bridge Service",
            5002: "Self-Learn Service",
            9000: "Chat Server"
        }
        
        running_services = []
        failed_services = []
        
        for port, name in services.items():
            try:
                result = subprocess.run(
                    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"http://localhost:{port}"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                status = result.stdout.strip()
                if status == "200":
                    running_services.append(f"✅ {name} (Port {port})")
                    print(f"✅ {name} (Port {port}): RUNNING")
                else:
                    failed_services.append(f"❌ {name} (Port {port}): HTTP {status}")
                    print(f"❌ {name} (Port {port}): HTTP {status}")
            except Exception as e:
                failed_services.append(f"❌ {name} (Port {port}): {str(e)}")
                print(f"❌ {name} (Port {port}): ERROR - {str(e)}")
        
        self.analysis_results["services"] = {
            "running": running_services,
            "failed": failed_services,
            "operational_percentage": (len(running_services) / len(services)) * 100
        }
        
        print(f"\n📊 Service Status: {len(running_services)}/{len(services)} running ({self.analysis_results['services']['operational_percentage']:.0f}%)")
    
    def analyze_code_structure(self):
        """Analyze Aurora's code structure and organization"""
        print("\n" + "="*80)
        print("🏗️  ANALYZING CODE STRUCTURE")
        print("="*80)
        
        critical_files = {
            "aurora_core.py": "Core Intelligence System",
            "aurora_chat_server.py": "Chat Server",
            "chat_with_aurora.py": "Interactive Chat Interface",
            "x-start": "Service Launcher",
            "server/index.ts": "Backend Server",
            "server/aurora-chat.ts": "Chat Routes"
        }
        
        file_status = {}
        for file, description in critical_files.items():
            file_path = self.project_root / file
            if file_path.exists():
                size = file_path.stat().st_size
                file_status[file] = {
                    "exists": True,
                    "description": description,
                    "size": size,
                    "size_kb": f"{size/1024:.1f}KB"
                }
                print(f"✅ {file} ({size/1024:.1f}KB) - {description}")
            else:
                file_status[file] = {
                    "exists": False,
                    "description": description
                }
                print(f"❌ {file} - MISSING - {description}")
                self.analysis_results["issues"].append(f"Critical file missing: {file}")
        
        self.analysis_results["code_quality"]["critical_files"] = file_status
    
    def analyze_aurora_core(self):
        """Deep analysis of aurora_core.py"""
        print("\n" + "="*80)
        print("🧠 ANALYZING AURORA CORE INTELLIGENCE")
        print("="*80)
        
        try:
            from aurora_core import AuroraKnowledgeTiers, AuroraCoreIntelligence
            
            # Analyze tier structure
            tiers = AuroraKnowledgeTiers()
            
            core_analysis = {
                "foundation_count": tiers.foundation_count,
                "knowledge_tier_count": tiers.knowledge_tier_count,
                "total_tiers": tiers.total_tiers,
                "capabilities_count": tiers.capabilities_count,
                "hybrid_mode": tiers.hybrid_mode
            }
            
            print(f"📊 Foundation Tasks: {core_analysis['foundation_count']}")
            print(f"📊 Knowledge Tiers: {core_analysis['knowledge_tier_count']}")
            print(f"📊 Total Tiers: {core_analysis['total_tiers']}")
            print(f"📊 Capabilities: {core_analysis['capabilities_count']}")
            print(f"📊 Hybrid Mode: {core_analysis['hybrid_mode']}")
            
            self.analysis_results["architecture"]["core_intelligence"] = core_analysis
            
            # Test core functionality
            print("\n🧪 Testing Core Functions...")
            intelligence = AuroraCoreIntelligence()
            print("✅ AuroraCoreIntelligence initialized successfully")
            
        except Exception as e:
            error_msg = f"Aurora Core Error: {str(e)}\n{traceback.format_exc()}"
            print(f"❌ {error_msg}")
            self.analysis_results["issues"].append(error_msg)
    
    def analyze_python_environment(self):
        """Check Python packages and dependencies"""
        print("\n" + "="*80)
        print("🐍 ANALYZING PYTHON ENVIRONMENT")
        print("="*80)
        
        try:
            result = subprocess.run(
                ["pip3", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                
                # Check critical packages
                critical_packages = ["flask", "fastapi", "uvicorn", "flask-cors"]
                installed = {}
                missing = []
                
                for pkg in critical_packages:
                    found = next((p for p in packages if p["name"].lower() == pkg), None)
                    if found:
                        installed[pkg] = found["version"]
                        print(f"✅ {pkg} {found['version']}")
                    else:
                        missing.append(pkg)
                        print(f"❌ {pkg} - NOT INSTALLED")
                
                self.analysis_results["architecture"]["python_packages"] = {
                    "installed": installed,
                    "missing": missing,
                    "total_packages": len(packages)
                }
                
                if missing:
                    self.analysis_results["issues"].append(f"Missing packages: {', '.join(missing)}")
            
        except Exception as e:
            error_msg = f"Python environment check failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.analysis_results["issues"].append(error_msg)
    
    def analyze_performance(self):
        """Analyze system performance and resource usage"""
        print("\n" + "="*80)
        print("⚡ ANALYZING PERFORMANCE")
        print("="*80)
        
        try:
            # Get Aurora processes
            aurora_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'aurora' in cmdline.lower() or 'bridge' in cmdline.lower() or 'self_learn' in cmdline.lower():
                        aurora_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline[:100],
                            'memory_mb': proc.info['memory_info'].rss / 1024 / 1024
                        })
                        print(f"🔹 PID {proc.info['pid']}: {cmdline[:80]} ({proc.info['memory_info'].rss / 1024 / 1024:.1f}MB)")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # System resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            print(f"\n💻 System CPU: {cpu_percent}%")
            print(f"💾 System Memory: {memory.percent}% used ({memory.used/1024/1024/1024:.1f}GB / {memory.total/1024/1024/1024:.1f}GB)")
            print(f"💿 Disk Usage: {disk.percent}% used ({disk.used/1024/1024/1024:.1f}GB / {disk.total/1024/1024/1024:.1f}GB)")
            
            self.analysis_results["performance"] = {
                "aurora_processes": len(aurora_processes),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "processes": aurora_processes
            }
            
        except Exception as e:
            error_msg = f"Performance analysis failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.analysis_results["issues"].append(error_msg)
    
    def check_recent_errors(self):
        """Check for recent errors in log files"""
        print("\n" + "="*80)
        print("🔍 CHECKING FOR ERRORS")
        print("="*80)
        
        log_files = [
            "/tmp/aurora_chat.log",
            "/tmp/aurora_bridge.log",
            "/tmp/aurora_self_learn.log"
        ]
        
        errors_found = []
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-20:]  # Last 20 lines
                        for line in lines:
                            if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'failed']):
                                errors_found.append(f"{log_file}: {line.strip()}")
                                print(f"⚠️  {log_file}: {line.strip()}")
                except Exception as e:
                    print(f"⚠️  Could not read {log_file}: {str(e)}")
        
        if not errors_found:
            print("✅ No recent errors found in log files")
        
        self.analysis_results["issues"].extend(errors_found)
    
    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print("\n" + "="*80)
        print("💡 GENERATING RECOMMENDATIONS")
        print("="*80)
        
        recommendations = []
        
        # Service recommendations
        if self.analysis_results["services"]["operational_percentage"] < 100:
            recommendations.append("Some services are not running - check service logs and restart failed services")
        
        # Performance recommendations
        if self.analysis_results.get("performance", {}).get("memory_percent", 0) > 80:
            recommendations.append("High memory usage detected - consider optimizing or restarting services")
        
        # Code quality recommendations
        if len(self.analysis_results["issues"]) > 0:
            recommendations.append(f"Found {len(self.analysis_results['issues'])} issues - review and fix critical problems")
        
        if not recommendations:
            recommendations.append("System is operating optimally - no immediate actions required")
        
        self.analysis_results["recommendations"] = recommendations
        
        for rec in recommendations:
            print(f"💡 {rec}")
    
    def generate_summary(self):
        """Generate final summary"""
        print("\n" + "="*80)
        print("📋 AURORA SYSTEM ANALYSIS SUMMARY")
        print("="*80)
        
        operational = self.analysis_results["services"]["operational_percentage"]
        issues_count = len(self.analysis_results["issues"])
        
        if operational == 100 and issues_count == 0:
            status = "🟢 EXCELLENT"
        elif operational >= 75 and issues_count < 3:
            status = "🟡 GOOD"
        elif operational >= 50:
            status = "🟠 FAIR"
        else:
            status = "🔴 CRITICAL"
        
        print(f"\n**OVERALL STATUS: {status}**")
        print(f"**Operational: {operational:.0f}%**")
        print(f"**Issues Found: {issues_count}**")
        print(f"**Recommendations: {len(self.analysis_results['recommendations'])}**")
        
        # Architecture summary
        if "core_intelligence" in self.analysis_results["architecture"]:
            core = self.analysis_results["architecture"]["core_intelligence"]
            print(f"\n**Core Intelligence:**")
            print(f"  - {core['foundation_count']} Foundation Tasks")
            print(f"  - {core['knowledge_tier_count']} Knowledge Tiers")
            print(f"  - {core['total_tiers']} Total Tiers")
            print(f"  - {core['capabilities_count']} Capabilities")
        
        # Service summary
        print(f"\n**Services:**")
        for service in self.analysis_results["services"]["running"]:
            print(f"  {service}")
        for service in self.analysis_results["services"]["failed"]:
            print(f"  {service}")
        
        # Issues summary
        if issues_count > 0:
            print(f"\n**Issues Detected:**")
            for i, issue in enumerate(self.analysis_results["issues"][:5], 1):
                print(f"  {i}. {issue[:100]}")
            if issues_count > 5:
                print(f"  ... and {issues_count - 5} more")
        
        # Recommendations
        print(f"\n**Recommendations:**")
        for i, rec in enumerate(self.analysis_results["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        # Save results
        output_file = self.project_root / "AURORA_SELF_ANALYSIS_REPORT.json"
        with open(output_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        print(f"\n📄 Full report saved to: {output_file}")
    
    def run_complete_analysis(self):
        """Run all analysis components"""
        print("\n" + "="*80)
        print("🌟 AURORA DEEP SELF-ANALYSIS INITIATED")
        print("="*80)
        print(f"Timestamp: {self.analysis_results['timestamp']}")
        
        self.analyze_services()
        self.analyze_code_structure()
        self.analyze_aurora_core()
        self.analyze_python_environment()
        self.analyze_performance()
        self.check_recent_errors()
        self.generate_recommendations()
        self.generate_summary()
        
        print("\n" + "="*80)
        print("✅ AURORA DEEP SELF-ANALYSIS COMPLETE")
        print("="*80)

if __name__ == "__main__":
    analyzer = AuroraDeepAnalysis()
    analyzer.run_complete_analysis()
