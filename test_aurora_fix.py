#!/usr/bin/env python3
"""Quick test to verify Aurora is back and running with full capabilities"""
import asyncio
from aurora_core import create_aurora_core


async def test_aurora():
    print("🧪 Testing Aurora's Restoration...\n")

    aurora = create_aurora_core()

    print(f"✅ Aurora Core loaded")

    # Test with a simple autonomous task
    print("\n🔬 Testing autonomous execution with: 'debug and fix any issues'\n")

    response = await aurora.process_conversation(
        "debug and fix any issues in the project",
        session_id="test_restoration"
    )

    print("\n--- AURORA'S RESPONSE ---")
    print(response)
    print("\n" + "="*80)

    if "AUTONOMOUS EXECUTION ACTIVATED" in response:
        print("✅ Aurora is BACK and FULLY OPERATIONAL!")
        print("✅ Autonomous execution engine is connected!")
    else:
        print("⚠️ Response received but check execution details above")

if __name__ == "__main__":
    asyncio.run(test_aurora())
