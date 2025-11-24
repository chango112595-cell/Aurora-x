#!/usr/bin/env python3
"""
Aurora Complete UI & System Diagnosis
Checking everything: frontend, backend, ports, servers, routing, build status
"""

import subprocess
import os
import sys
from pathlib import Path
import json

print("=" * 80)
print("[SCAN] AURORA COMPLETE UI & SYSTEM DIAGNOSIS")
print("=" * 80)

# Check 1: Port Status
print("\n1️⃣ CHECKING ALL PORTS...")
ports_to_check = [5000, 5001, 5002, 5003, 5005, 5173]
active_ports = []

for port in ports_to_check:
    try:
        result = subprocess.run(
            ["powershell", "-Command",
                f"Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"   [OK] Port {port}: LISTENING")
            active_ports.append(port)
        else:
            print(f"   [ERROR] Port {port}: NOT LISTENING")
    except Exception as e:
        print(f"   [WARN]  Port {port}: Error checking - {e}")

# Check 2: Frontend Files
print("\n2️⃣ CHECKING FRONTEND FILES...")
frontend_files = [
    "client/src/main.tsx",
    "client/src/App.tsx",
    "client/src/pages/dashboard.tsx",
    "client/src/components/AuroraFuturisticDashboard.tsx",
    "client/index.html",
    "client/vite.config.ts",
    "client/package.json"
]

for file in frontend_files:
    if Path(file).exists():
        size = Path(file).stat().st_size
        print(f"   [OK] {file} ({size} bytes)")
    else:
        print(f"   [ERROR] {file} - MISSING!")

# Check 3: Backend Server Files
print("\n3️⃣ CHECKING BACKEND FILES...")
backend_files = [
    "server/index.ts",
    "server/routes.ts",
    "server/vite.ts",
    "package.json"
]

for file in backend_files:
    if Path(file).exists():
        size = Path(file).stat().st_size
        print(f"   [OK] {file} ({size} bytes)")
    else:
        print(f"   [ERROR] {file} - MISSING!")

# Check 4: Test Frontend Access
print("\n4️⃣ TESTING FRONTEND ACCESS...")
test_urls = [
    "http://localhost:5000/",
    "http://localhost:5000/dashboard",
    "http://localhost:5173/",
    "http://localhost:5173/dashboard"
]

for url in test_urls:
    try:
        result = subprocess.run(
            ["curl.exe", "-s", "-o", "nul", "-w", "%{http_code}", url],
            capture_output=True,
            text=True,
            timeout=5
        )
        status_code = result.stdout.strip()
        if status_code == "200":
            print(f"   [OK] {url} - HTTP {status_code}")
        else:
            print(f"   [WARN]  {url} - HTTP {status_code}")
    except Exception as e:
        print(f"   [ERROR] {url} - Error: {e}")

# Check 5: Check Dashboard Component Content
print("\n5️⃣ CHECKING DASHBOARD COMPONENT CONTENT...")
dashboard_file = Path("client/src/components/AuroraFuturisticDashboard.tsx")
if dashboard_file.exists():
    content = dashboard_file.read_text(encoding='utf-8')
    checks = {
        "188 TOTAL POWER": "188" in content,
        "66 Knowledge Tiers": "66</div>" in content,
        "109 Capability Modules": "109</div>" in content or "109 Capability" in content,
        "Hybrid Mode": "Hybrid Mode" in content or "hybrid" in content.lower()
    }
    for check, result in checks.items():
        if result:
            print(f"   [OK] {check}: Found")
        else:
            print(f"   [ERROR] {check}: NOT FOUND")
else:
    print("   [ERROR] Dashboard component file missing!")

# Check 6: Check Routing Configuration
print("\n6️⃣ CHECKING ROUTING CONFIGURATION...")
main_tsx = Path("client/src/main.tsx")
if main_tsx.exists():
    content = main_tsx.read_text(encoding='utf-8')
    if '/dashboard' in content:
        print(f"   [OK] Dashboard route configured in main.tsx")
    else:
        print(f"   [ERROR] Dashboard route NOT found in main.tsx")

    if 'Dashboard' in content:
        print(f"   [OK] Dashboard component imported")
    else:
        print(f"   [ERROR] Dashboard component NOT imported")

# Check 7: Check if Vite is serving
print("\n7️⃣ CHECKING VITE DEV SERVER...")
if 5173 in active_ports:
    print("   [OK] Vite dev server is running on port 5173")
    try:
        result = subprocess.run(
            ["curl.exe", "-s", "http://localhost:5173/"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "<!DOCTYPE html>" in result.stdout or "<html" in result.stdout:
            print("   [OK] Vite is serving HTML content")
        else:
            print("   [WARN]  Vite response doesn't look like HTML")
    except Exception as e:
        print(f"   [ERROR] Error testing Vite: {e}")
else:
    print("   [ERROR] Vite dev server NOT running!")

# Check 8: Check Backend Proxy
print("\n8️⃣ CHECKING BACKEND PROXY CONFIGURATION...")
if 5000 in active_ports:
    print("   [OK] Backend server running on port 5000")
    # Check if backend is proxying to Vite
    server_index = Path("server/index.ts")
    if server_index.exists():
        content = server_index.read_text(encoding='utf-8')
        if '5173' in content:
            print("   [OK] Backend references Vite port 5173")
        else:
            print("   [WARN]  Backend might not be proxying to Vite")
else:
    print("   [ERROR] Backend server NOT running!")

# Check 9: Check tmux sessions
print("\n9️⃣ CHECKING TMUX SESSIONS...")
try:
    result = subprocess.run(
        ["tmux", "list-sessions"],
        capture_output=True,
        text=True,
        timeout=5
    )
    if result.returncode == 0:
        sessions = result.stdout.strip().split('\n')
        aurora_sessions = [s for s in sessions if 'aurora' in s.lower()]
        if aurora_sessions:
            print(f"   [OK] Found {len(aurora_sessions)} Aurora tmux sessions")
            for session in aurora_sessions[:5]:
                print(f"      • {session[:80]}")
        else:
            print("   [WARN]  No Aurora tmux sessions found")
    else:
        print("   [WARN]  tmux not running or no sessions")
except Exception as e:
    print(f"   [WARN]  Cannot check tmux: {e}")

# Check 10: Check node_modules
print("\n[EMOJI] CHECKING NODE_MODULES...")
client_nm = Path("client/node_modules")
root_nm = Path("node_modules")

if client_nm.exists():
    print(f"   [OK] client/node_modules exists")
else:
    print(f"   [ERROR] client/node_modules MISSING - run 'cd client && npm install'")

if root_nm.exists():
    print(f"   [OK] node_modules exists")
else:
    print(f"   [ERROR] node_modules MISSING - run 'npm install'")

# Summary
print("\n" + "=" * 80)
print("[DATA] DIAGNOSIS SUMMARY")
print("=" * 80)
print(f"Active Ports: {len(active_ports)}/{len(ports_to_check)}")
print(f"Active Ports List: {active_ports}")
print()

if 5173 in active_ports and 5000 in active_ports:
    print("[OK] BOTH Vite (5173) and Backend (5000) are running")
    print()
    print("[WEB] Try accessing:")
    print("   • http://localhost:5000/dashboard")
    print("   • http://localhost:5173/dashboard")
    print()
    print("[IDEA] If still not visible:")
    print("   1. Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)")
    print("   2. Clear browser cache completely")
    print("   3. Try incognito/private window")
    print("   4. Check browser console (F12) for errors")
elif 5173 not in active_ports:
    print("[ERROR] PROBLEM: Vite dev server NOT running on port 5173")
    print("   Fix: Run 'cd client && npm run dev'")
elif 5000 not in active_ports:
    print("[ERROR] PROBLEM: Backend server NOT running on port 5000")
    print("   Fix: Run 'npm run dev' from root")
else:
    print("[ERROR] CRITICAL: Neither Vite nor Backend are running!")
    print("   Fix: Run 'npm run dev' from root to start both")

print("=" * 80)
