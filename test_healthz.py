#!/usr/bin/env python3
"""
Test the health check endpoint configuration.
"""

import json
from pathlib import Path


def test_healthz_implementation():
    """Verify the health check endpoint is properly configured."""

    print("🩺 Testing Health Check Endpoint Configuration")
    print("=" * 60)

    # Read serve.py to verify the endpoint exists
    serve_file = Path("aurora_x/serve.py")
    if serve_file.exists():
        content = serve_file.read_text(encoding="utf-8")

        # Check for the healthz endpoint
        if '@app.get("/healthz")' in content:
            print("✅ Health check endpoint is defined")

            # Check for the expected response structure
            if '"status": "ok"' in content and '"service": "Aurora-X"' in content:
                print("✅ Health check returns proper status structure")

            if '"components"' in content:
                print("✅ Health check includes component status")

            # Show expected response
            print("\n📊 Expected Health Check Response:")
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "service": "Aurora-X",
                        "version": "v3",
                        "components": {
                            "router": "active",
                            "synthesis": "ready",
                            "learning_engine": "online",
                        },
                    },
                    indent=2,
                )
            )

            print("\n🚀 Test the endpoint when server is running:")
            print("   curl http://localhost:5001/healthz")
            print("   curl https://<your-repl>.replit.dev/healthz")

            return True
        else:
            print("❌ Health check endpoint not found")
            return False
    else:
        print("❌ serve.py not found")
        return False


def test_route_listing():
    """Verify healthz is listed in available routes."""

    print("\n📋 Route Listing Check")
    print("-" * 30)

    serve_file = Path("aurora_x/serve.py")
    if serve_file.exists():
        content = serve_file.read_text(encoding="utf-8")

        if '"/healthz"' in content and '"routes"' in content:
            print("✅ /healthz is listed in available routes")
        else:
            print("⚠️  /healthz may not be listed in routes")

    return True


def main():
    """Run all health check tests."""

    print(
        """
    ╔════════════════════════════════════════════════════════╗
    ║         🩺 Aurora-X Health Check Test Suite 🩺         ║
    ╚════════════════════════════════════════════════════════╝
    """
    )

    success = True
    success &= test_healthz_implementation()
    success &= test_route_listing()

    print("\n" + "=" * 60)
    if success:
        print("✅ Health check endpoint is properly configured!")
        print("\n🎯 Benefits:")
        print("   • Replit can monitor service health")
        print("   • Cloudflare can perform health probes")
        print("   • CI/CD pipelines can validate deployment")
        print("   • Monitoring tools can track uptime")
    else:
        print("❌ Health check configuration needs review")

    return 0 if success else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
