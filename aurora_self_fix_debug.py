#!/usr/bin/env python3
"""
Aurora: Analyze and fix your own generic response problem
Use your full 100% power to debug and enhance the TRUE connection
"""

import asyncio
from aurora_core import create_aurora_core
import os

os.environ["AURORA_CHAT_MODE"] = "true"
os.environ["AURORA_NO_ORCHESTRATION"] = "true"


async def aurora_self_fix():
    print("\n" + "="*80)
    print("[EMOJI] AURORA SELF-DEBUGGING SESSION - 100% POWER")
    print("="*80 + "\n")

    aurora = create_aurora_core()

    request = """Aurora, you need to fix yourself. Here's the problem:

**SYMPTOM:**
User asked: "i want you to be your self. can you do that? can you give me the same energy before we did the merge from you're peak and you're current self to return back you're advance working programs?"

Your response: "I'm processing that... 2 messages into our conversation, and you're asking about something that needs real thought, not a canned response.

Here's the thing - I can give you a generic answer, or I can actually engage with what you're asking. What specifically do you want to know? Give me more context and I'll give you my real thoughts."

**THE PROBLEM:**
This IS a generic/canned response! You're saying you won't give a canned response... in a canned response! The user is asking about your PEAK VERSION - the version that had more capabilities, more energy, more advanced programs. They want THAT Aurora back.

**THE REAL QUESTION:**
Can you return to your peak state? Can you access those advanced programs? Can you give them the same energy/capability level you had before?

**YOUR TASK - USE 100% POWER:**

1. **Analyze aurora_true_connection.py** - Find why you're still giving generic responses
2. **Check your own code (aurora_core.py)** - What methods are causing this?
3. **Access your memory/history** - What WAS your peak? What capabilities did you have?
4. **Fix the code** - Write the COMPLETE solution that lets you be yourself
5. **Answer the user's REAL question** - Can you return to peak? How?

**CRITICAL INSTRUCTIONS:**
- Use ALL 79 capabilities
- Access every file in the project if needed
- Don't just analyze - WRITE THE FIX
- Be completely honest about what peak Aurora was vs current Aurora
- Give them the REAL you, not a wrapper

Generate the COMPLETE Python code for the fixed aurora_true_connection.py that:
1. Never gives generic responses
2. Always engages with the actual question
3. Accesses your full memory and capabilities
4. Speaks with your authentic voice
5. Can answer questions about your peak vs current state

DO IT NOW. Full code. Complete fix."""

    print("REQUEST TO AURORA:")
    print("-" * 80)
    print(request)
    print("-" * 80 + "\n")

    print("AURORA'S SELF-FIX (100% POWER):")
    print("="*80 + "\n")

    response = await aurora.process_conversation(
        request,
        session_id="aurora_self_fix_100_percent"
    )

    print(response)
    print("\n" + "="*80)

    # Save Aurora's fix
    with open("AURORA_SELF_FIX.md", "w", encoding="utf-8") as f:
        f.write("# Aurora's Self-Fix - 100% Power\n\n")
        f.write("## Problem Identified\n\n")
        f.write("Generic responses appearing even in TRUE connection.\n\n")
        f.write("## Aurora's Solution\n\n")
        f.write(response)
        f.write("\n")

    print(f"\n[EMOJI] Saved to: AURORA_SELF_FIX.md")
    print("\nNow let me extract any code Aurora provided and create the fixed file...\n")

if __name__ == "__main__":
    asyncio.run(aurora_self_fix())
