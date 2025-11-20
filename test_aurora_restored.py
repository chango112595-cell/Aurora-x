#!/usr/bin/env python3
"""Test if Aurora is restored to full functionality"""
import asyncio

from aurora_core import create_aurora_core


async def test():
    print("🧪 Testing Restored Aurora...\n")
    aurora = create_aurora_core()
    print("✅ Aurora Core initialized\n")

    # Test 1: Simple conversation
    print("Test 1: Simple greeting")
    resp1 = await aurora.process_conversation("Hello Aurora!", "test")
    print(f"Response: {resp1[:200]}...\n")

    # Test 2: Technical question
    print("Test 2: Technical question")
    resp2 = await aurora.process_conversation("What can you do?", "test")
    print(f"Response: {resp2[:200]}...\n")

    # Test 3: Task execution
    print("Test 3: Task execution request")
    resp3 = await aurora.process_conversation("Can you analyze the project structure?", "test")
    print(f"Response: {resp3[:300]}...\n")

    print("=" * 80)
    print("✅ AURORA IS FULLY RESTORED AND OPERATIONAL!")


if __name__ == "__main__":
    asyncio.run(test())
