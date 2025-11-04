#!/usr/bin/env python3
"""
Aurora Self-Diagnosis and Repair
=================================
Aurora diagnoses and fixes her own UI connection issues.
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List


class AuroraSelfRepair:
    """Aurora diagnoses and repairs herself."""
    
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.issues = []
        self.fixes = []
        
    async def diagnose_connections(self):
        """Diagnose connection refused errors."""
        print("🔍 AURORA SELF-DIAGNOSIS")
        print("=" * 70)
        print("Issue: Server Control shows 'Connection refused' for all services")
        print("=" * 70)
        
        print("\n📊 Step 1: Check which ports are actually listening")
        print("-" * 70)
        
        result = subprocess.run(
            ["lsof", "-i", "-P", "-n"],
            capture_output=True,
            text=True
        )
        
        listening_ports = {}
        for line in result.stdout.split('\n'):
            if 'LISTEN' in line:
                parts = line.split()
                for part in parts:
                    if ':' in part and part.count(':') == 1:
                        try:
                            port = part.split(':')[1]
                            if port.isdigit():
                                listening_ports[port] = line
                        except:
                            pass
        
        aurora_ports = ['5000', '5001', '5002', '8080', '9090']
        
        for port in aurora_ports:
            if port in listening_ports:
                print(f"   ✅ Port {port}: LISTENING")
            else:
                print(f"   ❌ Port {port}: NOT LISTENING")
                self.issues.append(f"Port {port} not listening")
        
        print("\n📊 Step 2: Check server-control page configuration")
        print("-" * 70)
        
        # Read the server control page
        server_control_files = [
            "client/src/pages/server-control.tsx",
            "client/src/pages/server-control-new.tsx"
        ]
        
        for file in server_control_files:
            path = self.root / file
            if path.exists():
                print(f"\n   Checking: {file}")
                content = path.read_text()
                
                # Check for hardcoded URLs
                if 'localhost' in content:
                    print(f"   ⚠️  Found 'localhost' - may need to use correct host")
                    
                # Look for API endpoints
                if 'http://' in content:
                    import re
                    urls = re.findall(r'http://[^\s\'"]+', content)
                    for url in urls[:5]:  # Show first 5
                        print(f"      URL: {url}")
                        
        print("\n📊 Step 3: Identify the root cause")
        print("-" * 70)
        
        # Aurora's analysis
        print("\n   Aurora's Analysis:")
        print("   🧠 The Server Control page is trying to connect to services")
        print("   🧠 But services are either:")
        print("      1. Not running on those ports")
        print("      2. Running but blocking connections")
        print("      3. Page using wrong URLs/ports")
        
        return True
    
    async def propose_fixes(self):
        """Aurora proposes fixes."""
        print("\n\n🔧 AURORA'S FIX PROPOSALS")
        print("=" * 70)
        
        fixes = {
            "fix_1": {
                "name": "Start missing services",
                "description": "Start Aurora backend services on correct ports",
                "commands": [
                    "Check which services should be running",
                    "Start Aurora backend on port 5001",
                    "Start learning server on port 5002", 
                    "Verify health endpoints"
                ]
            },
            "fix_2": {
                "name": "Update Server Control page URLs",
                "description": "Fix hardcoded URLs in server-control.tsx",
                "actions": [
                    "Use environment variables for API URLs",
                    "Add proper CORS configuration",
                    "Use /api proxy instead of direct URLs"
                ]
            },
            "fix_3": {
                "name": "Check health endpoints",
                "description": "Ensure all services have /health endpoints",
                "actions": [
                    "Add /health to aurora_x/serve.py",
                    "Add /health to chat server",
                    "Test health endpoints return 200 OK"
                ]
            }
        }
        
        for fix_id, fix in fixes.items():
            print(f"\n{fix_id.upper()}: {fix['name']}")
            print(f"   {fix['description']}")
            if 'commands' in fix:
                for cmd in fix['commands']:
                    print(f"      • {cmd}")
            if 'actions' in fix:
                for action in fix['actions']:
                    print(f"      • {action}")
        
        return fixes
    
    async def execute_fix_1(self):
        """Start missing services."""
        print("\n\n🚀 EXECUTING FIX 1: Start services")
        print("=" * 70)
        
        # Check aurora_x/serve.py
        serve_file = self.root / "aurora_x" / "serve.py"
        
        if not serve_file.exists():
            print("❌ aurora_x/serve.py not found")
            return False
        
        print("✅ Found aurora_x/serve.py")
        
        # Check if it has health endpoint
        content = serve_file.read_text()
        
        if '/health' not in content and '/healthz' not in content:
            print("⚠️  No /health endpoint found - Aurora will add it")
            
            # Aurora adds health endpoint
            health_endpoint = '''

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "aurora-backend",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/healthz")
async def healthz():
    """Alternative health check endpoint."""
    return {"status": "ok"}
'''
            
            # Find a good place to add it (after imports, before other routes)
            if 'from fastapi import FastAPI' in content:
                # Add after FastAPI import section
                import_end = content.find('\napp = FastAPI')
                if import_end == -1:
                    import_end = content.find('\ndef ')
                    
                if import_end != -1:
                    # Add datetime import if not present
                    if 'from datetime import datetime' not in content:
                        content = content.replace(
                            'from fastapi import FastAPI',
                            'from fastapi import FastAPI\nfrom datetime import datetime'
                        )
                    
                    # Add health endpoints after app creation
                    app_creation = content.find('app = FastAPI')
                    if app_creation != -1:
                        next_line = content.find('\n\n', app_creation)
                        if next_line != -1:
                            content = content[:next_line] + health_endpoint + content[next_line:]
                            
                            serve_file.write_text(content)
                            print("✅ Added /health and /healthz endpoints")
                            self.fixes.append("Added health endpoints to aurora_x/serve.py")
        else:
            print("✅ Health endpoint already exists")
        
        return True
    
    async def execute_fix_2(self):
        """Fix Server Control page URLs."""
        print("\n\n🔧 EXECUTING FIX 2: Update Server Control URLs")
        print("=" * 70)
        
        server_control = self.root / "client" / "src" / "pages" / "server-control.tsx"
        
        if not server_control.exists():
            print("❌ server-control.tsx not found")
            return False
        
        content = server_control.read_text()
        
        print("📝 Aurora is analyzing the Server Control page...")
        
        # Check what's wrong
        issues_found = []
        
        if 'localhost:5001' in content:
            issues_found.append("Hardcoded localhost:5001")
        if 'localhost:5002' in content:
            issues_found.append("Hardcoded localhost:5002")
        if 'localhost:8080' in content:
            issues_found.append("Hardcoded localhost:8080")
            
        if issues_found:
            print(f"\n   Found issues:")
            for issue in issues_found:
                print(f"      ⚠️  {issue}")
            
            print("\n   Aurora's recommendation:")
            print("      Use relative URLs to proxy through Vite dev server")
            print("      Example: '/api/health' instead of 'http://localhost:5001/health'")
            
        else:
            print("   ✅ No hardcoded localhost URLs found")
        
        return True
    
    async def check_service_status(self):
        """Check actual service status."""
        print("\n\n📊 SERVICE STATUS CHECK")
        print("=" * 70)
        
        services = [
            {"name": "Aurora UI", "port": 5000, "process": "vite"},
            {"name": "Aurora Backend", "port": 5001, "process": "uvicorn"},
            {"name": "Learning Server", "port": 5002, "process": "python"},
        ]
        
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        
        for service in services:
            running = False
            for line in result.stdout.split('\n'):
                if str(service['port']) in line and service['process'] in line:
                    running = True
                    break
            
            status = "✅ RUNNING" if running else "❌ NOT RUNNING"
            print(f"   {service['name']}: {status}")
            
            if not running:
                self.issues.append(f"{service['name']} not running")
        
        return True
    
    async def repair(self):
        """Main repair process."""
        await self.diagnose_connections()
        fixes = await self.propose_fixes()
        await self.check_service_status()
        
        print("\n\n✨ AURORA'S REPAIR PLAN")
        print("=" * 70)
        
        print("\n🎯 What Aurora will do:")
        print("   1. ✅ Add health endpoints to backend services")
        print("   2. 🔍 Identify URL configuration issues")
        print("   3. 📋 Provide specific fixes for Server Control page")
        
        # Execute fixes Aurora can do
        await self.execute_fix_1()
        await self.execute_fix_2()
        
        print("\n\n📋 NEXT STEPS FOR USER")
        print("=" * 70)
        print("\nAurora needs you to:")
        print("   1. Check if backend services are running:")
        print("      $ lsof -i :5001")
        print("      $ lsof -i :5002")
        print()
        print("   2. If not running, start them:")
        print("      $ cd /workspaces/Aurora-x")
        print("      $ python -m uvicorn aurora_x.serve:app --port 5001 --reload &")
        print()
        print("   3. Check Server Control page is using correct URLs")
        print("      - Should use relative URLs like /api/health")
        print("      - Not hardcoded http://localhost:5001")
        print()
        print("   4. Refresh the UI and test connections")
        
        if self.fixes:
            print("\n✅ Fixes Aurora applied:")
            for fix in self.fixes:
                print(f"   • {fix}")
        
        return True


async def main():
    """Let Aurora repair herself."""
    aurora = AuroraSelfRepair()
    await aurora.repair()
    
    print("\n\n" + "=" * 70)
    print("✨ Aurora self-diagnosis complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
