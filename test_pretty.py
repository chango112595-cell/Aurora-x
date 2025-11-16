#!/usr/bin/env python
"""Test the /api/solve/pretty endpoint with human-friendly output"""

import json


def test_pretty_locally():
    """Test pretty formatting without server"""
    from aurora_x.chat.attach_pretty import _fmt_seconds
    from aurora_x.generators.solver import solve_text

    test_cases = [
        "orbital period a=7000 km M=5.972e24 kg",
        "orbital period a=42164 km M=5.972e24 kg",
        "orbital period a=1 AU M=1.989e30 kg",
        "differentiate 3x^2 + 2x + 5",
        "2 + 3 * 4",  # Just the expression for evaluation
    ]

    print("Testing Pretty Formatting Locally:\n")

    for problem in test_cases:
        print(f"Problem: {problem}")
        result = solve_text(problem)

        if result.get("ok"):
            pretty = None
            if result.get("kind") == "physics.orbital_period":
                sec = float(result["period_s"])
                pretty = f"Orbital period: {_fmt_seconds(sec)}"
            elif result.get("kind") == "physics.em_superposition":
                x, y, z = result["result"]
                pretty = f"Field vector sum: ({x:.3f}, {y:.3f}, {z:.3f})"
            elif result.get("kind") == "math.evaluate":
                pretty = f"Value = {result['value']:.12g}"
            elif result.get("kind") == "math.differentiate":
                pretty = f"d/dx → {result['derivative']}"

            print(f"  ✓ Pretty: {pretty}")
            print(f"  Raw: {json.dumps(result, indent=2)[:100]}...")
        else:
            print(f"  ✗ Error: {result}")

        print()


def test_api():
    """Test the API endpoint"""
    import requests

    base_url = "http://localhost:5001"

    test_cases = [
        {"problem": "orbital period a=7000 km M=5.972e24 kg"},
        {"problem": "orbital period a=42164 km M=5.972e24 kg"},
        {"problem": "differentiate 3x^2 + 2x + 5"},
        {"problem": "2 + 3 * 4"},  # Just the expression for evaluation
    ]

    print("\nTesting /api/solve/pretty endpoint:\n")

    for tc in test_cases:
        print(f"Problem: {tc['problem']}")

        try:
            resp = requests.post(
                f"{base_url}/api/solve/pretty",
                json=tc,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if resp.status_code == 200:
                result = resp.json()
                if result.get("pretty"):
                    print(f"  ✓ Pretty: {result['pretty']}")
                else:
                    print("  ⚠ No pretty text returned")
            else:
                print(f"  ✗ Error: Status {resp.status_code}")
                print(f"     Response: {resp.text}")
        except requests.exceptions.ConnectionError:
            print("  ⚠ API not running - testing locally only")
        except Exception as e:
            print(f"  ✗ Error: {e}")

        print()


if __name__ == "__main__":
    print("=" * 60)
    print("T09 PRETTY FORMATTER TEST")
    print("=" * 60)
    print()

    # Test locally first (doesn't need server)
    test_pretty_locally()

    # Then test API if server is running
    test_api()

    print("\n✨ Pretty formatting examples:")
    print('  "orbital period a=7000 km M=5.972e24 kg" → "Orbital period: 1.60 hours"')
    print('  "orbital period a=42164 km M=5.972e24 kg" → "Orbital period: 23.93 hours"')
    print('  "differentiate 3x^2 + 2x + 5" → "d/dx → 6*x + 2"')
    print('  "evaluate 2 + 3 * 4" → "Value = 14"')
