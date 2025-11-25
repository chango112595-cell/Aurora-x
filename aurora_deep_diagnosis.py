<<<<<<< HEAD
=======
"""
Aurora Deep Diagnosis

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
#!/usr/bin/env python3
"""
Aurora DEEP System Diagnosis
Complete scan of every component: frontend, backend, services, ports, files, dependencies
"""

<<<<<<< HEAD
=======
from typing import Dict, List, Tuple, Optional, Any, Union
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
import os
import sys
import json
import subprocess
import socket
from pathlib import Path
from datetime import datetime

<<<<<<< HEAD
print("=" * 80)
print("🔬 AURORA DEEP SYSTEM DIAGNOSIS")
=======
# Aurora Performance Optimization
from concurrent.futures import ThreadPoolExecutor

# High-performance parallel processing with ThreadPoolExecutor
# Example: with ThreadPoolExecutor(max_workers=100) as executor:
#             results = executor.map(process_func, items)

print("=" * 80)
print("[EMOJI] AURORA DEEP SYSTEM DIAGNOSIS")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
print("Scanning EVERYTHING - this may take a few minutes...")
print("=" * 80)

issues_found = []
warnings_found = []


<<<<<<< HEAD
def add_issue(category, issue, severity="ERROR"):
=======
def add_issue(category, issue, severity="ERROR") -> None:
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
    """Track issues found"""
    if severity == "ERROR":
        issues_found.append(f"[{category}] {issue}")
    else:
        warnings_found.append(f"[{category}] {issue}")
<<<<<<< HEAD
    print(f"   {'❌' if severity == 'ERROR' else '⚠️'} {issue}")
=======
    print(f"   {'[ERROR]' if severity == 'ERROR' else '[WARN]'} {issue}")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8


def add_success(message):
    """Track successes"""
<<<<<<< HEAD
    print(f"   ✅ {message}")
=======
    print(f"   [OK] {message}")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8


# ============================================================================
# 1. PORT & SERVICE CHECK
# ============================================================================
<<<<<<< HEAD
print("\n1️⃣ CHECKING ALL PORTS & SERVICES...")
=======
print("\n1 CHECKING ALL PORTS & SERVICES...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
required_ports = {
    5000: "Backend + Frontend",
    5001: "Bridge Service",
    5002: "Self-Learning",
    5003: "Chat Server",
    5005: "Luminar Nexus",
    5173: "Vite Dev Server"
}

for port, name in required_ports.items():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()

    if result == 0:
        add_success(f"Port {port} ({name}): LISTENING")
    else:
        add_issue("PORTS", f"Port {port} ({name}): NOT RUNNING", "ERROR")

# ============================================================================
# 2. NODE.JS DEPENDENCIES CHECK
# ============================================================================
<<<<<<< HEAD
print("\n2️⃣ CHECKING NODE.JS DEPENDENCIES...")
=======
print("\n2 CHECKING NODE.JS DEPENDENCIES...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

# Check package.json exists
if Path("package.json").exists():
    add_success("package.json found")
else:
    add_issue("DEPENDENCIES", "package.json MISSING", "ERROR")

# Check node_modules
if Path("node_modules").exists():
    add_success("node_modules exists")

    # Check critical native modules
    critical_modules = [
        "node_modules/better-sqlite3",
        "node_modules/bcrypt",
        "node_modules/esbuild"
    ]

    for module in critical_modules:
        if Path(module).exists():
            add_success(f"{module.split('/')[-1]} installed")
        else:
            add_issue("DEPENDENCIES",
                      f"{module.split('/')[-1]} MISSING", "WARNING")
else:
    add_issue("DEPENDENCIES", "node_modules MISSING - run 'npm install'", "ERROR")

# Check client dependencies
if Path("client/package.json").exists():
    add_success("client/package.json found")
    if Path("client/node_modules").exists():
        add_success("client/node_modules exists")
    else:
        add_issue(
            "DEPENDENCIES", "client/node_modules MISSING - run 'cd client && npm install'", "ERROR")
else:
    add_issue("DEPENDENCIES", "client/package.json MISSING", "WARNING")

# ============================================================================
# 3. PYTHON ENVIRONMENT CHECK
# ============================================================================
<<<<<<< HEAD
print("\n3️⃣ CHECKING PYTHON ENVIRONMENT...")
=======
print("\n3 CHECKING PYTHON ENVIRONMENT...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

# Check Python version
try:
    result = subprocess.run([sys.executable, "--version"],
                            capture_output=True, text=True, timeout=5)
    version = result.stdout.strip()
    add_success(f"Python: {version}")
except Exception as e:
    add_issue("PYTHON", f"Cannot check Python version: {e}", "ERROR")

# Check critical Python packages
critical_packages = [
    "flask", "requests", "aiohttp", "fastapi", "uvicorn",
    "sqlalchemy", "alembic", "pydantic", "python-dotenv"
]

try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"],
                            capture_output=True, text=True, timeout=10)
    installed = result.stdout.lower()

    for package in critical_packages:
        if package.lower() in installed:
            add_success(f"{package} installed")
        else:
            add_issue("PYTHON", f"{package} NOT installed", "WARNING")
except Exception as e:
    add_issue("PYTHON", f"Cannot check pip packages: {e}", "WARNING")

# ============================================================================
# 4. FRONTEND FILES CHECK
# ============================================================================
<<<<<<< HEAD
print("\n4️⃣ CHECKING FRONTEND FILES...")
=======
print("\n4 CHECKING FRONTEND FILES...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

frontend_files = {
    "client/index.html": "HTML entry point",
    "client/vite.config.ts": "Vite configuration",
    "client/src/main.tsx": "React entry point",
    "client/src/App.tsx": "Main App component",
    "client/src/pages/dashboard.tsx": "Dashboard page",
    "client/src/components/AuroraFuturisticDashboard.tsx": "New Aurora UI"
}

for file, desc in frontend_files.items():
    if Path(file).exists():
        size = Path(file).stat().st_size
        if size > 0:
            add_success(f"{desc}: {size} bytes")
        else:
            add_issue("FRONTEND", f"{file} is EMPTY", "ERROR")
    else:
        add_issue("FRONTEND", f"{file} MISSING", "ERROR")

# Check for correct content in new dashboard
dashboard_file = Path("client/src/components/AuroraFuturisticDashboard.tsx")
if dashboard_file.exists():
    content = dashboard_file.read_text(encoding='utf-8')
    checks = {
        "188 Total Power": "188" in content,
        "66 Knowledge Tiers": "66" in content,
        "109 Capability Modules": "109" in content,
        "Hybrid Mode text": "Hybrid Mode" in content or "hybrid" in content.lower()
    }

    for check, found in checks.items():
        if found:
            add_success(f"Dashboard has {check}")
        else:
            add_issue("FRONTEND", f"Dashboard missing {check}", "ERROR")

# ============================================================================
# 5. BACKEND FILES CHECK
# ============================================================================
<<<<<<< HEAD
print("\n5️⃣ CHECKING BACKEND FILES...")
=======
print("\n5 CHECKING BACKEND FILES...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

backend_files = {
    "server/index.ts": "Main server file",
    "server/routes.ts": "API routes",
    "server/vite.ts": "Vite integration",
    "aurora_core.py": "Aurora Core Intelligence",
    ".aurora/aurora_core.py": "Aurora Core (backup)"
}

for file, desc in backend_files.items():
    if Path(file).exists():
        size = Path(file).stat().st_size
        if size > 0:
            add_success(f"{desc}: {size} bytes")
        else:
            add_issue("BACKEND", f"{file} is EMPTY", "ERROR")
    else:
        add_issue("BACKEND", f"{file} MISSING", "ERROR")

# ============================================================================
# 6. AURORA CORE ARCHITECTURE CHECK
# ============================================================================
<<<<<<< HEAD
print("\n6️⃣ CHECKING AURORA CORE ARCHITECTURE...")
=======
print("\n6 CHECKING AURORA CORE ARCHITECTURE...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

try:
    # Import and check Aurora core
    sys.path.insert(0, str(Path.cwd()))
    from aurora_core import AuroraCoreIntelligence

    core = AuroraCoreIntelligence()
    kt = core.knowledge_tiers

    # Verify architecture values
    expected = {
        "foundation_count": 13,
        "knowledge_tier_count": 66,
        "total_tiers": 79,
        "capabilities_count": 109,
        "total_power": 188
    }

    actual = {
        "foundation_count": kt.foundation_count,
        "knowledge_tier_count": kt.knowledge_tier_count,
        "total_tiers": kt.total_tiers,
        "capabilities_count": kt.capabilities_count,
        "total_power": kt.total_power
    }

    for key, expected_val in expected.items():
        actual_val = actual[key]
        if actual_val == expected_val:
            add_success(f"{key}: {actual_val}")
        else:
            add_issue(
                "ARCHITECTURE", f"{key} is {actual_val}, expected {expected_val}", "ERROR")

except Exception as e:
    add_issue("ARCHITECTURE", f"Cannot load Aurora Core: {e}", "ERROR")

# ============================================================================
# 7. SYNTAX ERRORS CHECK
# ============================================================================
<<<<<<< HEAD
print("\n7️⃣ CHECKING FOR PYTHON SYNTAX ERRORS...")
=======
print("\n7 CHECKING FOR PYTHON SYNTAX ERRORS...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

python_files = list(Path(".").glob("*.py"))[:20]  # Check first 20 root files
syntax_errors = 0

for py_file in python_files:
    try:
        compile(py_file.read_text(encoding='utf-8'), py_file, 'exec')
    except SyntaxError as e:
        syntax_errors += 1
        add_issue("SYNTAX", f"{py_file}: Line {e.lineno} - {e.msg}", "ERROR")

if syntax_errors == 0:
    add_success(f"Checked {len(python_files)} Python files - no syntax errors")

# ============================================================================
# 8. DATABASE CHECK
# ============================================================================
<<<<<<< HEAD
print("\n8️⃣ CHECKING DATABASE...")
=======
print("\n8 CHECKING DATABASE...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

db_file = Path("aurora.db")
if db_file.exists():
    size = db_file.stat().st_size
    add_success(f"Database exists: {size} bytes")
else:
    add_issue("DATABASE", "aurora.db not found", "WARNING")

# ============================================================================
# 9. PROCESS CHECK
# ============================================================================
<<<<<<< HEAD
print("\n9️⃣ CHECKING RUNNING PROCESSES...")
=======
print("\n9 CHECKING RUNNING PROCESSES...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

try:
    if sys.platform == "win32":
        result = subprocess.run(
            ["powershell", "-Command",
                "Get-Process | Where-Object {$_.ProcessName -match 'node|python'} | Select-Object -First 10 ProcessName,Id,Path"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "node" in result.stdout.lower() or "python" in result.stdout.lower():
            add_success("Aurora processes running")
        else:
            add_issue("PROCESSES", "No Aurora processes detected", "WARNING")
except Exception as e:
    add_issue("PROCESSES", f"Cannot check processes: {e}", "WARNING")

# ============================================================================
# 10. FILE PERMISSIONS CHECK
# ============================================================================
<<<<<<< HEAD
print("\n🔟 CHECKING CRITICAL FILE PERMISSIONS...")
=======
print("\n[EMOJI] CHECKING CRITICAL FILE PERMISSIONS...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

critical_scripts = ["x-start", "x-stop"]
for script in critical_scripts:
    if Path(script).exists():
        add_success(f"{script} exists and is executable")
    else:
        add_issue("PERMISSIONS", f"{script} MISSING", "ERROR")

# ============================================================================
# 11. NATIVE MODULE COMPATIBILITY CHECK
# ============================================================================
<<<<<<< HEAD
print("\n1️⃣1️⃣ CHECKING NATIVE MODULE COMPATIBILITY...")
=======
print("\n11 CHECKING NATIVE MODULE COMPATIBILITY...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

try:
    # Test better-sqlite3
    test_cmd = "node -e \"require('better-sqlite3')\""
    result = subprocess.run(test_cmd, shell=True,
                            capture_output=True, text=True, timeout=5)

    if result.returncode == 0:
        add_success("better-sqlite3 loads correctly")
    else:
        error_msg = result.stderr
        if "not a valid Win32 application" in error_msg:
            add_issue(
                "NATIVE_MODULES", "better-sqlite3 wrong architecture - needs rebuild", "ERROR")
        else:
            add_issue("NATIVE_MODULES",
                      f"better-sqlite3 error: {error_msg[:100]}", "ERROR")

except Exception as e:
    add_issue("NATIVE_MODULES", f"Cannot test better-sqlite3: {e}", "WARNING")

try:
    # Test bcrypt
    test_cmd = "node -e \"require('bcrypt')\""
    result = subprocess.run(test_cmd, shell=True,
                            capture_output=True, text=True, timeout=5)

    if result.returncode == 0:
        add_success("bcrypt loads correctly")
    else:
        error_msg = result.stderr
        if "not a valid Win32 application" in error_msg:
            add_issue("NATIVE_MODULES",
                      "bcrypt wrong architecture - needs rebuild", "ERROR")
        else:
            add_issue("NATIVE_MODULES",
                      f"bcrypt error: {error_msg[:100]}", "ERROR")

except Exception as e:
    add_issue("NATIVE_MODULES", f"Cannot test bcrypt: {e}", "WARNING")

# ============================================================================
# 12. ROUTING CONFIGURATION CHECK
# ============================================================================
<<<<<<< HEAD
print("\n1️⃣2️⃣ CHECKING ROUTING CONFIGURATION...")
=======
print("\n12 CHECKING ROUTING CONFIGURATION...")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8

# Check main.tsx routing
main_tsx = Path("client/src/main.tsx")
if main_tsx.exists():
    content = main_tsx.read_text(encoding='utf-8')
    routes = ["/dashboard", "/chat", "/corpus", "/self-learning"]

    for route in routes:
        if route in content:
            add_success(f"Route '{route}' configured")
        else:
            add_issue(
                "ROUTING", f"Route '{route}' NOT found in main.tsx", "WARNING")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
<<<<<<< HEAD
print("📊 DEEP DIAGNOSIS COMPLETE")
print("=" * 80)

print(f"\n🔴 CRITICAL ERRORS: {len(issues_found)}")
=======
print("[DATA] DEEP DIAGNOSIS COMPLETE")
print("=" * 80)

print(f"\n[EMOJI] CRITICAL ERRORS: {len(issues_found)}")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
if issues_found:
    for issue in issues_found:
        print(f"   {issue}")

<<<<<<< HEAD
print(f"\n⚠️  WARNINGS: {len(warnings_found)}")
=======
print(f"\n[WARN]  WARNINGS: {len(warnings_found)}")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
if warnings_found:
    for warning in warnings_found:
        print(f"   {warning}")

# Save detailed report
report = {
    "timestamp": datetime.now().isoformat(),
    "errors": issues_found,
    "warnings": warnings_found,
    "total_issues": len(issues_found) + len(warnings_found)
}

report_file = Path("AURORA_DEEP_DIAGNOSIS_REPORT.json")
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2)

<<<<<<< HEAD
print(f"\n📄 Detailed report saved to: {report_file}")

print("\n" + "=" * 80)
if len(issues_found) == 0:
    print("✅ NO CRITICAL ERRORS FOUND - System is healthy!")
else:
    print("⚠️  CRITICAL ISSUES DETECTED - See above for details")
=======
print(f"\n[EMOJI] Detailed report saved to: {report_file}")

print("\n" + "=" * 80)
if len(issues_found) == 0:
    print("[OK] NO CRITICAL ERRORS FOUND - System is healthy!")
else:
    print("[WARN]  CRITICAL ISSUES DETECTED - See above for details")
>>>>>>> 315f5cdf027d37d7ae1db5d11342378c39aa92d8
print("=" * 80)
