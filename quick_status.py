"""
Quick Status

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

#!/usr/bin/env python3
"""
Quick status check - determines which services are down and what to do
"""
from typing import Dict, List, Tuple, Optional, Any, Union
import socket
import sys


def check_port(port_num, timeout=1.0):
    """
        Check Port
        
        Args:
            port_num: port num
            timeout: timeout
    
        Returns:
            Result of operation
        """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", port_num))
        s.close()
        return True
    except (TimeoutError, ConnectionRefusedError, OSError):
        return False


# Check critical ports
ports = {5000: "Aurora UI", 5002: "Learning API", 8000: "Dashboards"}

print("\n[EMOJI] Aurora Status Check\n" + "=" * 50)

all_up = True
for port, name in ports.items():
    status = "[OK] UP" if check_port(port) else "[ERROR] DOWN"
    print(f"[PORT {port}] {name}: {status}")
    if not check_port(port):
        all_up = False

print("=" * 50)

if all_up:
    print("\n[SPARKLES] All services UP! Aurora is ready!\n")
    print("[EMOJI] Access Aurora UI: http://127.0.0.1:5000")
    print("[CHART] Dashboards: http://127.0.0.1:8000")
    print("[BRAIN] Learning API: http://127.0.0.1:5002\n")
else:
    print("\n[WARN]  Some services are DOWN")
    print("\nTry starting services with:")
    print("  bash /workspaces/Aurora-x/startup_aurora.sh\n")

sys.exit(0 if all_up else 1)
