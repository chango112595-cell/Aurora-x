#!/usr/bin/env python3
"""
Ask Aurora to check all port status
"""

import asyncio
from aurora_core import AuroraCoreIntelligence
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    print("🌟 Asking Aurora to Check Port Status\n")
    aurora = AuroraCoreIntelligence()

    question = """
    Aurora, check the status of all your ports:
    - Port 5000 (Frontend)
    - Port 5001 (Bridge)
    - Port 5002 (Self-Learn)
    - Port 5173 (Vite Frontend)
    - Port 9000 (Chat Server)
    
    For each port, check if it's running and what service is on it.
    Give me a complete status report.
    """

    print("❓ Request to Aurora:")
    print("="*80)
    print(question)
    print("="*80 + "\n")

    # Use process_conversation to get response
    response = await aurora.process_conversation(question, "port_check")

    print("🌟 Aurora's Response:")
    print("="*80)
    print(response)
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
