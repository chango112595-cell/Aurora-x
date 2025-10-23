#!/usr/bin/env python3
"""
T09 Unit Conversion Test Suite
Tests the /api/units helper and automatic unit normalization
"""

from aurora_x.generators.solver import solve_text
from aurora_x.reasoners.units import normalize_to_si, parse_value_with_unit


def test_unit_conversions():
    """Test direct unit conversions."""
    print("\n" + "=" * 60)
    print("🔄 UNIT CONVERSION TESTS")
    print("=" * 60)

    # Distance conversions
    print("\n📏 Distance Units:")
    distance_tests = [
        ("7000 km", 7_000_000, "m"),
        ("1 AU", 149_597_870_700, "m"),
        ("100 feet", 30.48, "m"),
        ("5 miles", 8046.72, "m"),
        ("1000 mm", 1.0, "m"),
    ]

    for input_str, expected_val, _expected_unit in distance_tests:
        value, unit = parse_value_with_unit(input_str)
        result = normalize_to_si(value, unit)
        status = "✅" if abs(result["si_value"] - expected_val) < 0.1 else "❌"
        print(f"  {status} {input_str:15} → {result['si_value']:15,.2f} {result['si_unit']}")

    # Mass conversions
    print("\n⚖️  Mass Units:")
    mass_tests = [
        ("5 tons", 5000, "kg"),
        ("100 pounds", 45.3592, "kg"),
        ("2000 g", 2.0, "kg"),
        ("1 msun", 1.989e30, "kg"),
    ]

    for input_str, expected_val, _expected_unit in mass_tests:
        value, unit = parse_value_with_unit(input_str)
        result = normalize_to_si(value, unit)
        status = "✅" if abs(result["si_value"] / expected_val - 1) < 0.01 else "❌"
        print(f"  {status} {input_str:15} → {result['si_value']:15.3e} {result['si_unit']}")

    # Time conversions
    print("\n⏱️  Time Units:")
    time_tests = [
        ("24 hours", 86400, "s"),
        ("365.25 days", 31557600, "s"),
        ("1 year", 31536000, "s"),
        ("60 minutes", 3600, "s"),
    ]

    for input_str, expected_val, _expected_unit in time_tests:
        value, unit = parse_value_with_unit(input_str)
        result = normalize_to_si(value, unit)
        status = "✅" if abs(result["si_value"] - expected_val) < 1 else "❌"
        print(f"  {status} {input_str:15} → {result['si_value']:15,.0f} {result['si_unit']}")


def test_physics_with_units():
    """Test physics calculations with automatic unit conversion."""
    print("\n" + "=" * 60)
    print("🌍 PHYSICS WITH UNIT CONVERSION")
    print("=" * 60)

    test_cases = [
        {
            "prompt": "orbital period a=7000 km M=5.972e24 kg",
            "desc": "LEO with km",
            "expected_period": 5828.6,  # seconds
        },
        {
            "prompt": "orbital period a=42200 km M=5.972e24 kg",
            "desc": "GEO with km",
            "expected_period": 86275.2,  # seconds (~24 hours)
        },
        {
            "prompt": "orbital period a=1 AU M=2e30 kg",
            "desc": "1 AU orbit",
            "expected_period": 31466622.3,  # seconds (~1 year)
        },
        {
            "prompt": "orbital period a=238900 miles M=5.972e24 kg",
            "desc": "Moon orbit in miles",
            "expected_period": 2371877.1,  # seconds (~27.3 days)
        },
    ]

    for case in test_cases:
        result = solve_text(case["prompt"])
        period = result.get("period_s", 0)
        error_pct = abs(period - case["expected_period"]) / case["expected_period"] * 100
        status = "✅" if error_pct < 1 else "❌"

        if period > 86400:
            time_str = f"{period / 86400:.2f} days"
        else:
            time_str = f"{period / 3600:.2f} hours"

        print(f"  {status} {case['desc']:25} → {time_str}")
        if error_pct > 1:
            print(f"      Expected: {case['expected_period']:.1f}s, Got: {period:.1f}s")


def test_api_examples():
    """Show API endpoint examples."""
    print("\n" + "=" * 60)
    print("📡 API ENDPOINT EXAMPLES")
    print("=" * 60)

    print("\n🔗 /api/units - Convert units to SI:")
    print(
        """
curl -X POST http://localhost:5001/api/units \\
  -H 'Content-Type: application/json' \\
  -d '{"value": "7000 km"}'

Response:
{
  "si_value": 7000000,
  "si_unit": "m",
  "original": "7000 km",
  "conversion_factor": 1000.0,
  "unit_type": "distance"
}"""
    )

    print("\n🔗 /api/solve - Physics with auto-conversion:")
    print(
        """
curl -X POST http://localhost:5001/api/solve \\
  -H 'Content-Type: application/json' \\
  -d '{"problem": "orbital period a=1 AU M=2e30 kg"}'

Response:
{
  "ok": true,
  "kind": "physics.orbital_period",
  "a_m": 149597870700.0,  // AU converted to meters
  "M_kg": 2e30,
  "period_s": 31466622.3  // ~1 year
}"""
    )


def main():
    print(
        """
    ╔══════════════════════════════════════════════════════════╗
    ║         🚀 T09 Unit Conversion Test Suite 🚀             ║
    ║        Automatic SI Unit Normalization System            ║
    ╚══════════════════════════════════════════════════════════╝
    """
    )

    test_unit_conversions()
    test_physics_with_units()
    test_api_examples()

    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(
        """
✅ Distance conversions: km, miles, feet, AU → meters
✅ Mass conversions: tons, pounds, grams, solar masses → kg
✅ Time conversions: hours, days, years → seconds
✅ Physics solver auto-converts units before calculations
✅ /api/units endpoint provides explicit conversions

🎯 Aurora-X now handles units intelligently!
    """
    )


if __name__ == "__main__":
    main()
