#!/usr/bin/env python
"""Test the /api/format/seconds endpoint"""


def test_formatter_locally():
    """Test the formatter function locally"""
    from aurora_x.chat.attach_format import _fmt_seconds

    test_cases = [
        (45, "45.00 s"),
        (60, "1.00 min"),
        (90, "1.50 min"),
        (3600, "1.00 hours"),
        (5400, "1.50 hours"),
        (86400, "1.00 days"),
        (172800, "2.00 days"),
        (31536000, "365.00 days"),
        (31536001, "1.00 years"),
        (63072000, "2.00 years"),
    ]

    print("Testing Seconds Formatter Locally:\n")
    all_passed = True

    for seconds, expected in test_cases:
        result = _fmt_seconds(seconds)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_passed = False
        print(f"  {status} {seconds:>10} s → {result:15} (expected: {expected})")

    return all_passed


def test_api():
    """Test the API endpoint"""
    import requests

    base_url = "http://localhost:5001"

    test_cases = [
        {"seconds": 60, "expected": "1.00 min"},
        {"seconds": 3600, "expected": "1.00 hours"},
        {"seconds": 86400, "expected": "1.00 days"},
        {"seconds": 31536000, "expected": "365.00 days"},
        {"seconds": 5837.776554, "expected": "1.62 hours"},  # ISS orbit
        {"seconds": 86164.78605, "expected": "23.93 hours"},  # GEO orbit
    ]

    print("\nTesting /api/format/seconds endpoint:\n")

    for tc in test_cases:
        print(f"  Seconds: {tc['seconds']}")

        try:
            resp = requests.post(
                f"{base_url}/api/format/seconds",
                json={"seconds": tc["seconds"]},
                headers={"Content-Type": "application/json"},
            )

            if resp.status_code == 200:
                result = resp.json()
                if result.get("formatted"):
                    print(f"    ✓ Formatted: {result['formatted']}")
                    if result["formatted"] == tc["expected"]:
                        print(f"    ✓ Matches expected: {tc['expected']}")
                    else:
                        print(f"    ⚠ Expected: {tc['expected']}")
                else:
                    print("    ⚠ No formatted text returned")
            else:
                print(f"    ✗ Error: Status {resp.status_code}")
                print(f"       Response: {resp.text}")
        except requests.exceptions.ConnectionError:
            print("    ⚠ API not running - testing locally only")
        except Exception as e:
            print(f"    ✗ Error: {e}")

        print()


if __name__ == "__main__":
    print("=" * 60)
    print("T09 SECONDS FORMATTER TEST")
    print("=" * 60)
    print()

    # Test locally first
    if test_formatter_locally():
        print("\n✅ All local tests passed!")
    else:
        print("\n⚠ Some local tests failed")

    # Then test API if server is running
    test_api()

    print("\n✨ Usage Examples:")
    print()
    print("curl -X POST http://localhost:5001/api/format/seconds \\")
    print('  -H "Content-Type: application/json" \\')
    print("  -d '{\"seconds\": 86400}'")
    print('# Returns: {"ok": true, "formatted": "1.00 days"}')
    print()
    print("curl -X POST http://localhost:5001/api/format/seconds \\")
    print('  -H "Content-Type: application/json" \\')
    print("  -d '{\"seconds\": 3661.5}'")
    print('# Returns: {"ok": true, "formatted": "1.02 hours"}')
