#!/usr/bin/env python3
"""
Direct interaction with Aurora Core to ask what she's lacking
"""

import asyncio
from aurora_core import create_aurora_core


async def main():
    print("🧠 Initializing Aurora Core...")
    aurora = create_aurora_core()
    print("✅ Aurora initialized\n")

    question = "Aurora, what are you lacking on?"

    print(f"\nQuestion: {question}")
    print('='*80)

    response = await aurora.process_conversation(question, session_id="self_analysis")
    print(response)
    print('='*80)

if __name__ == "__main__":
    asyncio.run(main())
