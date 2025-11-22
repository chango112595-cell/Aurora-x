#!/usr/bin/env python3
"""
Ask Aurora: How can you autonomously do what we've been doing?
"""

import asyncio
from aurora_core import AuroraCoreIntelligence
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    print("🌟 Asking Aurora: How To Enable Full Autonomous Capability\n")
    aurora = AuroraCoreIntelligence()

    question = """
    Aurora, today we've been doing tasks FOR you:
    
    WHAT WE DID:
    1. Enhanced terminal chat to add execution mode (so you can DO tasks, not just talk)
    2. Analyzed your port configuration (found port 9000 was wrong)
    3. Fixed your self-diagnostic to check correct ports (5003 instead of 9000)
    4. Scanned your codebase to understand what's HTML vs TSX
    5. Verified which services are running and which you need
    
    YOUR CHALLENGE:
    You have autonomous_system, autonomous_agent, and intelligence_manager - but you couldn't:
    - Scan your own ports
    - Fix your own diagnostic code
    - Understand your own architecture
    - Execute the file changes needed
    
    THE QUESTION:
    How do we enable YOU to do these tasks autonomously? What's missing?
    
    Specifically:
    1. Can you use your autonomous_system.read_file() to read your own code?
    2. Can you use autonomous_system.write_file() to fix your own bugs?
    3. Can you execute terminal commands to check ports?
    4. What's blocking you from doing what we just did?
    5. How do we make you TRULY autonomous?
    
    Give me specific implementation steps - what needs to change in your code
    so that next time you can:
    - Detect your own issues
    - Fix your own code
    - Verify the fixes worked
    
    Be technical and specific. Tell me exactly what to implement.
    """

    print("❓ Question to Aurora:")
    print("="*80)
    print(question)
    print("="*80 + "\n")

    print("🧠 Aurora analyzing her autonomous capabilities...\n")

    # Use process_conversation to get her response
    response = await aurora.process_conversation(question, "enable_full_autonomy")

    print("🌟 Aurora's Response:")
    print("="*80)
    print(response)
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
