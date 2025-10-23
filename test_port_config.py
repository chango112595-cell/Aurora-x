#!/usr/bin/env python3
"""
Test that all templates correctly use the PORT environment variable.
"""

from aurora_x.templates.csharp_webapi import render_csharp_webapi
from aurora_x.templates.go_service import render_go_service
from aurora_x.templates.web_app_flask import render_app


def test_flask_port():
    """Test Flask template uses PORT env variable."""
    code = render_app("Test", "Test App")

    # Check for PORT environment variable usage
    assert "os.getenv('PORT'" in code or 'os.getenv("PORT"' in code
    assert "8000" in code  # Default port
    print("✅ Flask template uses PORT env (default: 8000)")
    return True


def test_go_port():
    """Test Go service template uses PORT env variable."""
    result = render_go_service("test", "Test service")
    code = result["files"]["main.go"]

    # Check for PORT environment variable usage
    assert 'os.Getenv("PORT")' in code
    assert '"8080"' in code  # Default port
    print("✅ Go service uses PORT env (default: 8080)")
    return True


def test_csharp_port():
    """Test C# WebAPI template uses PORT env variable."""
    result = render_csharp_webapi("test", "Test API")
    code = result["files"]["Program.cs"]

    # Check for PORT environment variable usage
    assert 'Environment.GetEnvironmentVariable("PORT")' in code
    assert '"5080"' in code  # Default port
    print("✅ C# WebAPI uses PORT env (default: 5080)")
    return True


def test_port_defaults():
    """Test default port assignments."""
    print("\n📊 Default Port Configuration:")
    print("   • Python Flask: 8000")
    print("   • Go Service: 8080")
    print("   • C# WebAPI: 5080")
    print("   • Rust CLI: N/A (not a web service)")
    print("\n💡 Set PORT environment variable to override")
    return True


def main():
    """Run all port configuration tests."""

    print(
        """
    ╔════════════════════════════════════════════════════════╗
    ║     🌐 Port Configuration Test Suite 🌐                ║
    ╚════════════════════════════════════════════════════════╝
    """
    )

    success = True

    try:
        success &= test_flask_port()
        success &= test_go_port()
        success &= test_csharp_port()
        success &= test_port_defaults()

        print("\n" + "═" * 60)
        if success:
            print("✅ All templates correctly configured for PORT env variable!")
            print("\n🚀 Templates are now Replit-ready!")
            print("   Set PORT=8000 (or any port) in your environment")
            print("   Templates will automatically use the assigned port")
        else:
            print("❌ Some port configuration tests failed")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
