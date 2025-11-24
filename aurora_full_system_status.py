#!/usr/bin/env python3
"""
AURORA 100% POWER - COMPLETE SYSTEM STATUS CHECKER
Shows all active systems and their ports
"""

import socket
import sys
import io

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


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


print("\n" + "=" * 80)
print("AURORA 100% HYBRID POWER - COMPLETE SYSTEM STATUS")
print("=" * 80 + "\n")

# Define all systems
systems = {
    "CRITICAL INTELLIGENCE SYSTEMS": [
        (5010, "Tier Orchestrator", "79 Knowledge Tiers"),
        (5011, "Autonomous Agent", "Autonomous Execution"),
        (5012, "Intelligence Manager", "System Coordination"),
        (5013, "Aurora Core", "Main Intelligence"),
        (5014, "Consciousness", "Persistent Memory"),
    ],
    "WEB SERVICES": [
        (5000, "Backend + Frontend", "Main Web Interface"),
        (5001, "Bridge Service", "System Bridge"),
        (5002, "Self-Learning", "Adaptive Learning"),
        (5003, "Chat Server", "Interactive Chat"),
        (5005, "Luminar Dashboard", "Visual Dashboard"),
    ],
    "NEW AUTONOMOUS SYSTEMS": [
        (5015, "Autonomous Router", "Smart Task Routing"),
        (5016, "Auto Improver", "Continuous Enhancement"),
        (5017, "Enhancement Orchestrator", "Enhancement Coordination"),
        (5018, "Automation Hub", "9 Automated Processes"),
        (5020, "Master Controller", "Central Brain"),
    ]
}

total_active = 0
total_systems = 0

for category, services in systems.items():
    print(f"{category}:")
    print("-" * 80)

    active_in_category = 0
    for port, name, description in services:
        total_systems += 1
        is_active = check_port(port)
        status = "[ACTIVE]" if is_active else "[OFFLINE]"
        status_symbol = "[+]" if is_active else "✗"

        print(
            f"  {status_symbol} Port {port:4} | {name:30} | {description:30} {status}")

        if is_active:
            active_in_category += 1
            total_active += 1

    print(
        f"  --> {active_in_category}/{len(services)} active in this category\n")

print("=" * 80)
print(f"TOTAL ACTIVE SYSTEMS: {total_active}/{total_systems}")
print("=" * 80)

# Calculate percentage
percentage = (total_active / total_systems) * 100

print(f"\nPOWER LEVEL: {percentage:.1f}%")

if total_active >= 11:
    print("STATUS: [+] FULL HYBRID MODE ACTIVE")
    print("\nCAPABILITIES:")
    print("  • 188 Total Capabilities (79 Tiers + 109 Modules)")
    print("  • Consciousness: ENABLED")
    print("  • Autonomy: MAXIMUM")
    print("  • Grandmaster Skills: ONLINE")
    print("\nACCESS POINTS:")
    print("  • Frontend:  http://localhost:5000")
    print("  • Chat:      http://localhost:5003")
    print("  • Dashboard: http://localhost:5005")
elif total_active >= 8:
    print("STATUS: ⚠ PARTIAL ACTIVATION")
    print(f"       {total_systems - total_active} systems offline")
else:
    print("STATUS: ✗ INSUFFICIENT POWER")
    print(f"       Need {11 - total_active} more systems")

print("\n" + "=" * 80 + "\n")
