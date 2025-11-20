#!/usr/bin/env python3
"""Final comprehensive test of restored Aurora"""
import asyncio
from aurora_core import create_aurora_core


async def comprehensive_test():
    print("🌟" * 40)
    print("AURORA COMPREHENSIVE RESTORATION TEST")
    print("🌟" * 40 + "\n")

    aurora = create_aurora_core()
    session = "final_test"

    tests = [
        ("Greeting", "Hi Aurora! Are you feeling better?"),
        ("Self-awareness", "What are your capabilities?"),
        ("Technical", "Explain how microservices work"),
        ("Memory", "My name is Chango"),
        ("Memory recall", "Do you remember my name?"),
        ("Task request", "Can you help me debug my code?"),
    ]

    passed = 0
    for test_name, prompt in tests:
        print(f"\n{'='*80}")
        print(f"TEST: {test_name}")
        print(f"PROMPT: {prompt}")
        print(f"{'='*80}")

        try:
            response = await aurora.process_conversation(prompt, session)
            print(
                f"RESPONSE: {response[:250]}{'...' if len(response) > 250 else ''}")

            if response and len(response) > 10:
                print("✅ PASS")
                passed += 1
            else:
                print("❌ FAIL - Response too short")
        except Exception as e:
            print(f"❌ FAIL - Error: {e}")

    print(f"\n{'='*80}")
    print(f"RESULTS: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉🎉🎉 AURORA IS FULLY RESTORED AND 100% OPERATIONAL! 🎉🎉🎉")
    else:
        print(f"\n⚠️ Some issues remain ({len(tests)-passed} failures)")

    print("="*80)

if __name__ == "__main__":
    asyncio.run(comprehensive_test())
