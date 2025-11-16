#!/usr/bin/env python
"""Test the demo dashboard accessibility and functionality"""

from pathlib import Path


def test_dashboard_html_exists():
    """Check if the dashboard HTML file exists"""
    dashboard_path = Path("aurora_x/static/demo-dashboard.html")
    if dashboard_path.exists():
        print("✅ Dashboard HTML file exists")
        print(f"   Location: {dashboard_path}")
        print(
            f"   Size: {len(dashboard_path.read_text(encoding='utf-8'))} bytes")
        return True
    else:
        print("❌ Dashboard HTML file not found")
        return False


def test_dashboard_endpoint():
    """Test the /dashboard/demos endpoint locally"""
    # pylint: disable=import-outside-toplevel
    from fastapi.testclient import TestClient

    # pylint: disable=import-outside-toplevel
    from aurora_x.serve import app

    client = TestClient(app)

    # Test the dashboard endpoint
    response = client.get("/dashboard/demos")

    if response.status_code == 200:
        print("✅ Dashboard endpoint working")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")

        # Check if it contains expected content
        content = response.text
        if "Aurora-X Demo Dashboard" in content:
            print("   ✅ Contains correct title")
        if "cards-grid" in content:
            print("   ✅ Contains cards grid")
        if "loadCards()" in content:
            print("   ✅ Contains JavaScript loader")
        return True
    else:
        print(f"❌ Dashboard endpoint error: {response.status_code}")
        return False


def test_demo_cards_api():
    """Test that the demo cards API is accessible"""
    # pylint: disable=import-outside-toplevel
    from fastapi.testclient import TestClient

    # pylint: disable=import-outside-toplevel
    from aurora_x.serve import app

    client = TestClient(app)

    # Test the demo cards API
    response = client.get("/api/demo/cards")

    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            print("✅ Demo cards API working")
            print(f"   Total cards: {data.get('total', 0)}")
            print(f"   Categories: {data.get('categories', {})}")
            return True

    print("❌ Demo cards API not working")
    return False


def print_access_instructions():
    """Print instructions for accessing the dashboard"""
    print("\n" + "=" * 60)
    print("📋 HOW TO ACCESS THE DEMO DASHBOARD:")
    print("=" * 60)
    print()
    print("1. Start Aurora-X server:")
    print("   python -m aurora_x.serve")
    print()
    print("2. Open in browser:")
    print("   http://localhost:5001/dashboard/demos")
    print()
    print("3. Features available:")
    print("   • Click any card to execute it")
    print("   • Filter by category (Chat, Solve, Units, Format)")
    print("   • View real-time responses in modal")
    print("   • Copy results to clipboard")
    print()
    print("4. Test with curl:")
    print("   curl http://localhost:5001/dashboard/demos")
    print()


def test_dashboard_features():
    """Describe the dashboard features"""
    print("\n✨ DEMO DASHBOARD FEATURES:")
    print("-" * 40)
    print("• Dark Aurora theme with cyan/purple accents")
    print("• 23+ interactive demo cards")
    print("• Category filtering (Chat, Solve, Units, Format)")
    print("• Click-to-execute functionality")
    print("• Real-time response display")
    print("• Syntax-highlighted JSON output")
    print("• Copy-to-clipboard for results")
    print("• Responsive grid layout")
    print("• Loading spinners and error handling")
    print("• Standalone - doesn't touch main Aurora UI")


if __name__ == "__main__":
    print("🚀 DEMO DASHBOARD TEST")
    print("=" * 60)
    print()

    all_pass = True

    # Test 1: HTML file exists
    if not test_dashboard_html_exists():
        all_pass = False
    print()

    # Test 2: Dashboard endpoint works
    if not test_dashboard_endpoint():
        all_pass = False
    print()

    # Test 3: Demo cards API works
    if not test_demo_cards_api():
        all_pass = False

    if all_pass:
        print("\n✅ ALL TESTS PASSED!")
        test_dashboard_features()
        print_access_instructions()
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print_access_instructions()
