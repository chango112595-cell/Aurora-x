#!/usr/bin/env python3
"""
Ask Aurora: Do we need the chat server on port 9000?
"""

import asyncio
from aurora_core import AuroraCoreIntelligence
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    print("🌟 Asking Aurora About Port 9000 Chat Server\n")
    aurora = AuroraCoreIntelligence()

    question = """
    Aurora, analyze port 9000 and the aurora_chat_server.py:
    
    CURRENT SITUATION:
    - Port 9000 is NOT running (shows as ❌ in your self-diagnostic)
    - aurora_chat_server.py defaults to port 9000
    - It's described as "Chat Server" but we also have:
      - Port 5173 (Vite Frontend) 
      - Port 5000 (Frontend)
      - Terminal chat (chat_with_aurora.py) which talks to you directly
    
    QUESTIONS:
    1. What is port 9000 / aurora_chat_server.py actually used for?
    2. Is it redundant now that we have enhanced terminal chat with execution mode?
    3. Do we need to start it, or can we deprecate it?
    4. What functionality would we lose if we don't run it?
    5. Is it part of your web UI, or is it a separate chat interface?
    
    Give me your architectural analysis: Should port 9000 be running, or is it obsolete?
    """

    print("❓ Question to Aurora:")
    print("="*80)
    print(question)
    print("="*80 + "\n")

    # Use process_conversation
    response = await aurora.process_conversation(question, "port_9000_analysis")

    print("🌟 Aurora's Analysis:")
    print("="*80)
    print(response)
    print("="*80)

    # Also check if the file exists and what it does
    print("\n📋 Quick File Check:")
    try:
        with open("aurora_chat_server.py", "r") as f:
            content = f.read()
            print(f"✓ aurora_chat_server.py exists ({len(content)} bytes)")
            print(
                f"✓ Imports: {'luminar_nexus_v2' if 'luminar_nexus_v2' in content else 'aurora_core only'}")
            print(
                f"✓ Default port: {9000 if '9000' in content else 'variable'}")
            print(f"✓ Flask server: {'Yes' if 'Flask' in content else 'No'}")
            print(
                f"✓ API endpoints: {content.count('@app.route')} routes defined")
    except FileNotFoundError:
        print("✗ aurora_chat_server.py not found")

if __name__ == "__main__":
    asyncio.run(main())
