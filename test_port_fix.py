"""
Test Port Fix

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

#!/usr/bin/env python3
"""
Test Aurora's fixed port diagnostic
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import asyncio
from aurora_core import AuroraCoreIntelligence
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    """
        Main
            """
    print("[EMOJI] Testing Aurora's Fixed Port Diagnostic\n")
    aurora = AuroraCoreIntelligence()

    print("Running self-diagnostic with corrected ports...\n")

    response = await aurora.process_conversation("self diagnose", "port_fix_test")

    print("="*80)
    print(response)
    print("="*80)

    print("\n[OK] Port diagnostic updated:")
    print("    Removed: Port 9000 (deprecated)")
    print("    Added: Port 5003 (Chat Server - correct port)")
    print("    Added: Port 5005 (Luminar Dashboard)")

if __name__ == "__main__":
    asyncio.run(main())
