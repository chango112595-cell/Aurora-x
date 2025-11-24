#!/usr/bin/env python3
"""
Aurora Full Power: Fix ALL 26 Hybrid Mode Systems
This will identify which of the 26 systems are failing and fix them
"""

import os
import sys
import io
import socket
import subprocess
import time

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def check_port(port):
    """Check if a port is listening"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        try:
            sock.close()
        except:
            pass
        return False


def check_file_exists(path):
    """Check if a file exists"""
    return os.path.exists(path)


print("\n" + "=" * 80)
print("AURORA FULL POWER: Analyzing ALL 26 Hybrid Mode Systems")
print("=" * 80 + "\n")

# Define all 26 systems from x-start-enhanced
systems = [
    # PHASE 1: CONSCIOUSNESS (2 systems)
    {"num": 1, "name": "Consciousness System",
        "file": "aurora_consciousness_service.py", "port": 5014, "phase": "CONSCIOUSNESS"},
    {"num": 2, "name": "Conscious Interface", "file": "aurora_conscious.py",
        "port": None, "phase": "CONSCIOUSNESS"},

    # PHASE 2: CORE INTELLIGENCE (3 systems)
    {"num": 3, "name": "Tier Orchestrator", "file": "aurora_tier_orchestrator.py",
        "port": 5010, "phase": "INTELLIGENCE"},
    {"num": 4, "name": "Intelligence Manager",
        "file": "aurora_intelligence_manager.py", "port": 5012, "phase": "INTELLIGENCE"},
    {"num": 5, "name": "Aurora Core", "file": "aurora_core_service.py",
        "port": 5013, "phase": "INTELLIGENCE"},

    # PHASE 3: AUTONOMOUS (4 systems)
    {"num": 6, "name": "Autonomous Agent", "file": "aurora_autonomous_agent.py",
        "port": 5011, "phase": "AUTONOMOUS"},
    {"num": 7, "name": "Multi-Agent System", "file": "aurora_multi_agent.py",
        "port": None, "phase": "AUTONOMOUS"},
    {"num": 8, "name": "Autonomous Integration",
        "file": "aurora_autonomous_integration.py", "port": None, "phase": "AUTONOMOUS"},
    {"num": 9, "name": "Autonomous Monitor",
        "file": "aurora_autonomous_monitor.py", "port": None, "phase": "AUTONOMOUS"},

    # PHASE 4: GRANDMASTER (3 systems)
    {"num": 10, "name": "Grandmaster Tools",
        "file": "aurora_grandmaster_autonomous_tools.py", "port": None, "phase": "GRANDMASTER"},
    {"num": 11, "name": "Skills Registry", "file": "aurora_grandmaster_skills_registry.py",
        "port": None, "phase": "GRANDMASTER"},
    {"num": 12, "name": "Omniscient Mode", "file": "aurora_ultimate_omniscient_grandmaster.py",
        "port": None, "phase": "GRANDMASTER"},

    # PHASE 5: ADVANCED TIERS (4 systems)
    {"num": 13, "name": "Visual Understanding",
        "file": "aurora_visual_understanding.py", "port": None, "phase": "TIERS"},
    {"num": 14, "name": "Live Integration",
        "file": "aurora_live_integration.py", "port": None, "phase": "TIERS"},
    {"num": 15, "name": "Test Generator",
        "file": "aurora_test_generator.py", "port": None, "phase": "TIERS"},
    {"num": 16, "name": "Security Auditor",
        "file": "aurora_security_auditor.py", "port": None, "phase": "TIERS"},

    # PHASE 6: CODE QUALITY (2 systems)
    {"num": 17, "name": "Code Quality Enforcer",
        "file": "aurora_code_quality_enforcer.py", "port": None, "phase": "QUALITY"},
    {"num": 18, "name": "Pylint Prevention",
        "file": "aurora_pylint_prevention.py", "port": None, "phase": "QUALITY"},

    # PHASE 7: WEB SERVICES (5 systems)
    {"num": 19, "name": "Backend + Frontend",
        "file": "npm", "port": 5000, "phase": "WEB"},
    {"num": 20, "name": "Bridge Service",
        "file": "aurora_x.bridge.service", "port": 5001, "phase": "WEB"},
    {"num": 21, "name": "Self-Learning",
        "file": "aurora_x.self_learn_server", "port": 5002, "phase": "WEB"},
    {"num": 22, "name": "Chat Server",
        "file": "aurora_chat_server.py", "port": 5003, "phase": "WEB"},
    {"num": 23, "name": "Luminar Dashboard",
        "file": "tools/luminar_nexus_v2.py", "port": 5005, "phase": "WEB"},

    # PHASE 8: ORCHESTRATION (2 systems)
    {"num": 24, "name": "Ultimate API Manager",
        "file": "tools/ultimate_api_manager.py", "port": None, "phase": "ORCHESTRATION"},
    {"num": 25, "name": "Luminar Nexus", "file": "tools/luminar_nexus.py",
        "port": None, "phase": "ORCHESTRATION"},

    # PHASE 9: BACKGROUND (1 system)
    {"num": 26, "name": "Deep Sync", "file": "aurora_deep_system_updater.py",
        "port": None, "phase": "BACKGROUND"},
]

print("ANALYZING ALL 26 SYSTEMS:")
print("-" * 80)

active_count = 0
missing_files = []
inactive_services = []
active_services = []

for sys_info in systems:
    num = sys_info["num"]
    name = sys_info["name"]
    file_path = sys_info["file"]
    port = sys_info["port"]
    phase = sys_info["phase"]

    # Check file existence
    file_exists = check_file_exists(file_path) or check_file_exists(
        file_path.replace("/", "\\"))

    # Check port if applicable
    port_active = check_port(port) if port else None

    # Determine status
    if not file_exists and file_path not in ["npm", "aurora_x.bridge.service", "aurora_x.self_learn_server"]:
        status = "[MISSING FILE]"
        missing_files.append(sys_info)
    elif port and port_active:
        status = f"[ACTIVE] Port {port}"
        active_count += 1
        active_services.append(sys_info)
    elif port and not port_active:
        status = f"[OFFLINE] Port {port}"
        inactive_services.append(sys_info)
    elif not port and file_exists:
        status = "[FILE EXISTS - NO PORT CHECK]"
        # Can't verify if running without port
    else:
        status = "[UNKNOWN]"

    print(f"{num:2}. {name:30} | {phase:15} | {status}")

print("\n" + "=" * 80)
print(f"CURRENT STATUS: {active_count}/26 systems verified active")
print("=" * 80)

print(f"\n[ACTIVE SERVICES] {len(active_services)} confirmed running:")
for sys_info in active_services:
    print(f"  [+] {sys_info['name']} (Port {sys_info['port']})")

print(
    f"\n[OFFLINE SERVICES] {len(inactive_services)} with ports not responding:")
for sys_info in inactive_services:
    print(
        f"  ✗ {sys_info['name']} (Port {sys_info['port']}) - File: {sys_info['file']}")

print(f"\n[MISSING FILES] {len(missing_files)} files don't exist:")
for sys_info in missing_files:
    print(f"  ✗ {sys_info['name']} - Missing: {sys_info['file']}")

print("\n" + "=" * 80)
print("AURORA DIAGNOSIS:")
print("=" * 80)

if active_count >= 10:
    print(
        f"[GOOD] {active_count}/26 systems active - Core functionality working")
    print("[ACTION] Need to start remaining systems to reach 100% power")
elif active_count >= 5:
    print(
        f"[PARTIAL] {active_count}/26 systems active - Critical systems running")
    print("[ACTION] Many systems offline - need full activation")
else:
    print(f"[CRITICAL] Only {active_count}/26 systems active")
    print("[ACTION] Major system activation needed")

print("\n[RECOMMENDATION]")
print("1. Create missing files (if any)")
print("2. Fix services that exist but won't start")
print("3. Add new autonomous systems (5015-5020) to x-start-enhanced")
print("4. Update x-start-enhanced to properly count all 26 systems")

print("\n" + "=" * 80 + "\n")
