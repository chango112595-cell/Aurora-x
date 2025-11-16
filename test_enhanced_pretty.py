#!/usr/bin/env python
"""Test the enhanced /api/solve/pretty endpoint with units formatting"""

import json

from aurora_x.chat.attach_pretty import _fmt_seconds
from aurora_x.chat.attach_units_format import _hint, _si_fmt
from aurora_x.generators.solver import solve_text


def test_enhanced_pretty_locally():
    """Test the enhanced pretty formatting locally"""

    test_cases = [
        "orbital period a=7000 km M=5.972e24 kg",
        "orbital period a=42164 km M=5.972e24 kg",
        "orbital period a=1 AU M=1.989e30 kg",
    ]

    print("Testing Enhanced Pretty Formatting with Units Info:\n")

    for problem in test_cases:
        print(f"Problem: {problem}")
        result = solve_text(problem)

        if result.get("ok") and result.get("kind") == "physics.orbital_period":
            sec = float(result["period_s"])
            pretty = f"Orbital period: {_fmt_seconds(sec)}"
            print(f"  ✓ Pretty: {pretty}")

            # Show units info
            print("  Units Info:")

            if "a_m" in result:
                a_fmt = _si_fmt(result["a_m"], "m")
                a_hint = _hint(result["a_m"], "m")
                print(f"    - Semi-major axis: {a_fmt}", end="")
                if a_hint:
                    print(f" ({a_hint})", end="")
                print()

            if "M_kg" in result:
                m_fmt = _si_fmt(result["M_kg"], "kg")
                m_hint = _hint(result["M_kg"], "kg")
                print(f"    - Central mass: {m_fmt}", end="")
                if m_hint:
                    print(f" ({m_hint})", end="")
                print()

            period_fmt = _si_fmt(sec, "s")
            print(f"    - Period: {period_fmt} = {_fmt_seconds(sec)}")
        else:
            print("  ✗ Error or non-physics problem")

        print()


def test_api_response_structure():
    """Test the API response structure"""
    import requests

    base_url = "http://localhost:5001"

    test_cases = [
        {"problem": "orbital period a=7000 km M=5.972e24 kg"},
        {"problem": "orbital period a=42164 km M=5.972e24 kg"},
    ]

    print("\nTesting Enhanced /api/solve/pretty Response Structure:\n")

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
                data = resp.json()
                if data.get("ok"):
                    print(f"  ✓ Pretty: {data.get('pretty')}")

                    if "units_info" in data:
                        print("  ✓ Units Info included:")
                        for item in data["units_info"]:
                            print(
                                f"    - {item['parameter']}: {item['pretty']}", end="")
                            if item.get("hint"):
                                print(f" ({item['hint']})", end="")
                            if item.get("human"):
                                print(f" = {item['human']}", end="")
                            print()
                    else:
                        print("  ⚠ No units_info in response")
                else:
                    print(f"  ✗ Error: {data}")
            else:
                print(f"  ✗ Error: Status {resp.status_code}")
                print(f"     Response: {resp.text}")
        except requests.exceptions.ConnectionError:
            print("  ⚠ API not running - testing locally only")
        except Exception as e:
            print(f"  ✗ Error: {e}")

        print()


def test_sample_output():
    """Show sample enhanced output"""
    print("\n📝 Sample Enhanced Output:\n")

    sample = {
        "ok": True,
        "pretty": "Orbital period: 1.62 hours",
        "result": {
            "ok": True,
            "kind": "physics.orbital_period",
            "a_m": 7000000.0,
            "M_kg": 5.972e24,
            "period_s": 5837.776554,
        },
        "units_info": [
            {
                "parameter": "Semi-major axis",
                "value": 7000000.0,
                "unit": "m",
                "pretty": "7 Mm",
                "hint": "LEO-ish altitude",
            },
            {
                "parameter": "Central mass",
                "value": 5.972e24,
                "unit": "kg",
                "pretty": "5.97e12 Tkg",
                "hint": "Mass of Earth",
            },
            {
                "parameter": "Period",
                "value": 5837.776554,
                "unit": "s",
                "pretty": "5.84 ks",
                "human": "1.62 hours",
            },
        ],
    }

    print(json.dumps(sample, indent=2))


if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED PRETTY ENDPOINT TEST")
    print("=" * 60)
    print()

    test_enhanced_pretty_locally()
    test_api_response_structure()
    test_sample_output()

    print("\n✨ Enhanced /api/solve/pretty now includes:")
    print("  • Human-readable period format")
    print("  • SI-formatted input parameters")
    print("  • Contextual hints for known constants")
    print("  • Full units_info array with all values")
    print()
    print("Example usage:")
    print("curl -X POST http://localhost:5001/api/solve/pretty \\")
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"problem": "orbital period a=7000 km M=5.972e24 kg"}\'')
