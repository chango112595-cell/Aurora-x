#!/usr/bin/env python
"""Test the updated /api/demo/cards endpoint"""

import asyncio
import json


def test_demo_cards_locally():
    """Test the updated demo cards structure locally"""
    from fastapi import FastAPI

    from aurora_x.chat.attach_demo import attach_demo

    app = FastAPI()
    attach_demo(app)

    async def get_cards():
        # Find the endpoint function
        for route in app.routes:
            if route.path == "/api/demo/cards":
                return await route.endpoint()
        return None

    result = asyncio.run(get_cards())

    if result:
        print("✅ Demo cards endpoint working!")
        print("\n📊 Statistics:")
        print(f"  Total cards: {result['total']}")
        print("  Categories breakdown:")
        for cat, count in result["categories"].items():
            print(f"    - {cat}: {count} cards")

        print("\n🎯 Sample Cards by Category:\n")

        # Group cards by category
        by_category = {}
        for card in result["cards"]:
            cat = (
                "chat"
                if "/chat" in card["endpoint"]
                else "solve"
                if "/solve" in card["endpoint"]
                else "units"
                if "/units" in card["endpoint"]
                else "format"
            )
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(card)

        # Show samples from each category
        for cat_name, cat_cards in by_category.items():
            print(f"  📁 {cat_name.upper()} ({len(cat_cards)} cards):")
            for card in cat_cards[:2]:  # Show first 2
                print(f"    • [{card['id']}] {card['title']}")
                print(f"      Endpoint: {card['method']} {card['endpoint']}")
                if "hint" in card:
                    print(f"      💡 {card['hint']}")
                if "expected" in card:
                    print(f"      Expected: {card['expected']}")
            if len(cat_cards) > 2:
                print(f"    ... and {len(cat_cards) - 2} more\n")
            else:
                print()

        # Verify structure
        print("📋 Structure Validation:")
        required_fields = ["id", "title", "endpoint", "method", "body"]
        sample_card = result["cards"][0]
        for field in required_fields:
            if field in sample_card:
                print(f"  ✅ Has '{field}' field")
            else:
                print(f"  ❌ Missing '{field}' field")

        return result
    else:
        print("❌ Failed to get demo cards")
        return None


def test_specific_card(card_id="solve_orbit_units"):
    """Test executing a specific card"""
    import asyncio

    from fastapi import FastAPI

    from aurora_x.chat.attach_demo import attach_demo

    app = FastAPI()
    attach_demo(app)

    async def get_cards():
        for route in app.routes:
            if route.path == "/api/demo/cards":
                return await route.endpoint()
        return None

    result = asyncio.run(get_cards())

    if not result:
        print("❌ Could not get cards")
        return

    # Find the specific card
    card = None
    for c in result["cards"]:
        if c["id"] == card_id:
            card = c
            break

    if not card:
        print(f"❌ Card '{card_id}' not found")
        return

    print(f"\n🧪 Testing Card: {card['title']}")
    print(f"  ID: {card['id']}")
    print(f"  Endpoint: {card['method']} {card['endpoint']}")
    print(f"  Body: {json.dumps(card['body'], indent=2)}")

    # Test locally for solve endpoints
    if "/solve" in card["endpoint"]:
        from aurora_x.generators.solver import solve_text

        problem = card["body"].get("problem", "")

        result = solve_text(problem)
        if result.get("ok"):
            print("  ✅ Local test successful!")
            print(f"  Result: {result}")
            if "expected" in card:
                print(f"  Expected: {card['expected']}")
        else:
            print(f"  ❌ Error: {result}")
    else:
        print(f"  ℹ️  Card type: {card['endpoint']} (not tested locally)")

    if "hint" in card:
        print(f"  💡 Hint: {card['hint']}")


def print_curl_commands():
    """Print example curl commands for testing"""
    print("\n📝 Example curl commands:\n")

    examples = [
        {
            "desc": "Get all demo cards",
            "cmd": "curl -s http://localhost:5001/api/demo/cards | jq .",
        },
        {
            "desc": "Run chat_timer_python card",
            "cmd": """curl -s -X POST -H 'Content-Type: application/json' \\
  -d '{"prompt": "make a futuristic timer ui", "lang": "python"}' \\
  http://localhost:5001/chat | jq .""",
        },
        {
            "desc": "Run solve_orbit_units card",
            "cmd": """curl -s -X POST -H 'Content-Type: application/json' \\
  -d '{"problem": "orbital period a=7000 km M=5.972e24 kg"}' \\
  http://localhost:5001/api/solve/pretty | jq .""",
        },
        {
            "desc": "Run fmt_units card",
            "cmd": """curl -s -X POST -H 'Content-Type: application/json' \\
  -d '{"value": 7e6, "unit": "m"}' \\
  http://localhost:5001/api/format/units | jq .""",
        },
    ]

    for ex in examples:
        print(f"# {ex['desc']}:")
        print(f"{ex['cmd']}\n")


if __name__ == "__main__":
    print("🚀 AURORA-X DEMO CARDS TEST")
    print("=" * 60)
    print()

    result = test_demo_cards_locally()

    if result:
        test_specific_card("solve_orbit_units")
        test_specific_card("chat_timer_python")

        print_curl_commands()

        print("\n✨ Demo Cards Ready!")
        print("  • 25+ test cards covering all endpoints")
        print("  • Chat synthesis examples (Python/Go/Rust/C#)")
        print("  • Math/Physics solver examples")
        print("  • Unit conversion & formatting")
        print("  • Each card includes method, body, and hints/expected values")
        print("\n💡 Tip: Run 'python -m aurora_x.serve' to start the API on port 5001")
