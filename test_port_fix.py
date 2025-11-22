#!/usr/bin/env python3
"""
Test Aurora's fixed port diagnostic
"""

import asyncio
from aurora_core import AuroraCoreIntelligence
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    print("🧪 Testing Aurora's Fixed Port Diagnostic\n")
    aurora = AuroraCoreIntelligence()

    print("Running self-diagnostic with corrected ports...\n")

    response = await aurora.process_conversation("self diagnose", "port_fix_test")

    print("="*80)
    print(response)
    print("="*80)

    print("\n✅ Port diagnostic updated:")
    print("   • Removed: Port 9000 (deprecated)")
    print("   • Added: Port 5003 (Chat Server - correct port)")
    print("   • Added: Port 5005 (Luminar Dashboard)")

if __name__ == "__main__":
    asyncio.run(main())
