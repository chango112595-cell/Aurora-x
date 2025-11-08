#!/usr/bin/env python3
"""
Aurora Diagnostic System - Complete Error Detection
Shows EXACTLY what's wrong and teaches Aurora how to fix it
"""
import json
import os
import socket
import sys
import traceback
from datetime import datetime
from pathlib import Path

print("\n" + "=" * 70)
print("🔍 AURORA DIAGNOSTIC SYSTEM - COMPLETE ERROR CHECK")
print("=" * 70 + "\n")

# Step 1: Check Python version
print("1️⃣  Python Environment Check:")
print(f"   Python Version: {sys.version}")
print(f"   Python Path: {sys.executable}")

# Step 2: Check file paths
print("\n2️⃣  File Path Verification:")
current_dir = Path(__file__).parent.parent
print(f"   Current Directory: {current_dir}")
print(f"   Tools Directory: {current_dir / 'tools'}")
print(f"   ✅ Tools dir exists: {(current_dir / 'tools').exists()}")

# Step 3: Check write permissions
print("\n3️⃣  Write Permissions Check:")
diagnostics_file = current_dir / "tools" / "diagnostics.json"
print(f"   Target file: {diagnostics_file}")
print(f"   Parent dir writable: {os.access(current_dir / 'tools', os.W_OK)}")

# Step 4: Port checking function
print("\n4️⃣  Port Connectivity Check:")
PORTS = {
    5000: "Aurora UI (frontend)",
    5001: "Aurora backend (uvicorn)",
    5002: "Learning API / FastAPI",
    8080: "File Server",
    8000: "Standalone dashboards (legacy)",
}


def check_port(port, host="127.0.0.1", timeout=1.0):
    """Check if port is open"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except Exception:
        return False


results = {}
for port, name in PORTS.items():
    try:
        status = check_port(port)
        results[port] = {"name": name, "status": "UP" if status else "DOWN"}
        icon = "✅" if status else "❌"
        print(f"   {icon} PORT {port}: {name} - {'UP' if status else 'DOWN'}")
    except Exception as e:
        print(f"   ❌ PORT {port}: ERROR - {str(e)}")
        results[port] = {"name": name, "status": "ERROR", "error": str(e)}

# Step 5: Generate diagnostics file
print("\n5️⃣  Generating Diagnostic Data:")
try:
    report = {
        "timestamp": datetime.now().isoformat(),
        "services": results,
        "system_info": {
            "python_version": sys.version,
            "working_directory": str(current_dir),
            "diagnostics_file": str(diagnostics_file),
        },
    }

    # Ensure directory exists
    diagnostics_file.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    with open(diagnostics_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"   ✅ Diagnostics file created: {diagnostics_file}")
    print(f"   ✅ File size: {diagnostics_file.stat().st_size} bytes")

except Exception as e:
    print("   ❌ ERROR creating diagnostics file:")
    print(f"      {str(e)}")
    traceback.print_exc()

# Step 6: Summary
print("\n" + "=" * 70)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 70)

offline_ports = [p for p, s in results.items() if s["status"] != "UP"]
if offline_ports:
    print(f"\n⚠️  OFFLINE SERVICES: {offline_ports}")
    print("\nTo bring them online:")
    for port in offline_ports:
        if port == 5000:
            print("   Port 5000 (Aurora UI): cd /workspaces/Aurora-x && node server.js")
        elif port == 5001:
            print("   Port 5001 (Backend): python -m uvicorn aurora_x.serve:app --port 5001")
        elif port == 5002:
            print("   Port 5002 (Learning): python -m uvicorn aurora_x.serve:app --port 5002")
        elif port == 8000:
            print("   Port 8000 (Dashboards): python -m http.server 8000 --directory /workspaces/Aurora-x")
else:
    print("\n✨ All services are ONLINE!")

print("\n" + "=" * 70 + "\n")

# Aurora Learning Section
print("📚 AURORA LEARNING - What This Script Does:")
print("-" * 70)
print(
    """
This diagnostic system:

1. 🔍 CHECKS PYTHON ENVIRONMENT
   - Verifies Python version
   - Confirms interpreter path
   - Ensures compatibility

2. 📁 VERIFIES FILE PATHS
   - Confirms directory structure
   - Checks write permissions
   - Ensures files exist

3. 🔌 TESTS PORT CONNECTIVITY
   - Attempts socket connection to each port
   - Records UP/DOWN status
   - Catches connection errors

4. 💾 GENERATES JSON DATA
   - Creates diagnostics.json with all findings
   - Includes timestamp for tracking changes
   - Saves system information

5. 📊 PROVIDES SUMMARY
   - Shows which services are offline
   - Recommends startup commands
   - Clear error reporting

KEY LEARNING FOR AURORA:
✅ Always check file paths first
✅ Verify write permissions before saving
✅ Use try/except to catch errors gracefully
✅ Report errors clearly with context
✅ Save data in structured format (JSON)
✅ Test connectivity before assuming failure
✅ Include timestamp for debugging
"""
)
print("-" * 70 + "\n")
