#!/usr/bin/env python3
"""
Have Aurora comprehensively analyze ALL ports and services in her system
"""

import asyncio
from aurora_core import AuroraCoreIntelligence
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    print("🔍 Aurora System-Wide Port & Service Analysis\n")
    aurora = AuroraCoreIntelligence()

    question = """
    Aurora, I need you to use your autonomous capabilities to scan your entire system and analyze ALL ports and services.
    
    YOUR TASK - USE YOUR AUTONOMOUS SYSTEM TO:
    
    1. SCAN THE CODEBASE:
       - Find all files that start servers or listen on ports
       - Search for port numbers (5000, 5001, 5002, 5003, 5173, 9000, etc.)
       - Identify what each service actually does
    
    2. ANALYZE x-start SCRIPT:
       - What ports does it try to start?
       - What services are configured?
    
    3. CHECK RUNNING PROCESSES:
       - What's actually running right now?
       - Use your autonomous system to check active ports
    
    4. ARCHITECTURAL ANALYSIS:
       For each port you find, tell me:
       - Port number
       - What service runs on it
       - What file/script starts it
       - Is it essential or optional?
       - Is it redundant with another service?
    
    5. RECOMMENDATION:
       - Which ports do we ACTUALLY need?
       - Which can be deprecated?
       - What's the minimal working configuration?
    
    I'm confused about port 9000 specifically - where did it come from and do we need it?
    
    Use your file scanning, code analysis, and autonomous capabilities to give me a complete port audit.
    """

    print("❓ Request to Aurora:")
    print("="*80)
    print(question)
    print("="*80 + "\n")

    print("🧠 Aurora analyzing system with autonomous capabilities...\n")

    # Analyze with full intelligence
    analysis = aurora.analyze_natural_language(question)
    context = aurora.get_conversation_context("complete_port_analysis")

    # This should be treated as a technical analysis task
    response = aurora.generate_aurora_response(analysis, context)

    print("🌟 Aurora's Complete Port Analysis:")
    print("="*80)
    print(response)
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
