#!/usr/bin/env python3
"""
T08 End-to-End Test Suite
Tests all language outputs from the /chat endpoint
"""

import os
from pathlib import Path

import requests

HOST = os.getenv("HOST", "http://localhost:5001")


def test_prompt(prompt, expected_lang, description):
    """Test a single prompt through the /chat endpoint."""
    print(f"\n{'=' * 60}")
    print(f"📝 Testing: {description}")
    print(f"   Prompt: '{prompt}'")
    print(f"   Expected Language: {expected_lang}")

    try:
        # Make the API call
        response = requests.post(f"{HOST}/chat", json={"prompt": prompt}, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"   Language: {data.get('lang', 'unknown')}")
            print(f"   Kind: {data.get('kind', 'unknown')}")

            if "file" in data:
                print(f"   File: {data['file']}")
            elif "files" in data:
                print(f"   Files: {', '.join(data['files'])}")

            print(f"   Hint: {data.get('hint', 'N/A')}")
            print(f"   Reason: {data.get('reason', 'N/A')}")

            # Verify the generated file exists
            if "file" in data:
                if Path(data["file"]).exists():
                    print(f"   ✅ Generated file exists: {data['file']}")
                else:
                    print(f"   ❌ Generated file missing: {data['file']}")

            return data
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_health_check():
    """Test the /healthz endpoint."""
    print("\n🩺 Testing Health Check Endpoint")
    print("-" * 40)

    try:
        response = requests.get(f"{HOST}/healthz", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check OK")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
            components = data.get("components", {})
            for comp, status in components.items():
                print(f"   • {comp}: {status}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def run_generated_app(file_path, lang, hint):
    """Try to run the generated application."""
    print(f"\n🚀 Testing Generated {lang} App")
    print("-" * 40)

    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False

    # Just verify the file has expected content
    content = Path(file_path).read_text()

    if lang == "python":
        if "PORT" in content and "8000" in content:
            print("✅ Python app uses PORT (default 8000)")
        if "Flask" in content:
            print("✅ Flask app generated correctly")

    elif lang == "go":
        if 'os.Getenv("PORT")' in content:
            print("✅ Go service uses PORT env")
        if "8080" in content:
            print("✅ Go defaults to port 8080")

    elif lang == "csharp":
        if 'Environment.GetEnvironmentVariable("PORT")' in content:
            print("✅ C# API uses PORT env")
        if "5080" in content:
            print("✅ C# defaults to port 5080")

    print(f"   Run Command: {hint}")
    return True


def main():
    """Run the complete T08 end-to-end test suite."""

    print(
        """
    ╔══════════════════════════════════════════════════════════╗
    ║         🚀 T08 End-to-End Test Suite 🚀                  ║
    ║     Language Router + PORT + Health Check                 ║
    ╚══════════════════════════════════════════════════════════╝
    """
    )

    print(f"🌐 Testing against: {HOST}")

    # Test health check first
    if not test_health_check():
        print("\n⚠️  Server might not be running. Start with: python -m uvicorn aurora_x.serve:app --port 5001")
        return 1

    # Test prompts for each language
    test_cases = [
        ("make a futuristic timer ui", "python", "Python Flask UI"),
        ("fast microservice web api", "go", "Go Microservice"),
        ("memory-safe cli to parse args", "rust", "Rust CLI Tool"),
        ("enterprise web api with health", "csharp", "C# Web API"),
    ]

    results = []
    for prompt, expected_lang, description in test_cases:
        result = test_prompt(prompt, expected_lang, description)
        if result:
            results.append(
                {
                    "description": description,
                    "lang": result.get("lang"),
                    "file": result.get("file") or result.get("files", [])[0] if result.get("files") else None,
                    "hint": result.get("hint"),
                    "success": True,
                }
            )
        else:
            results.append({"description": description, "success": False})

    # Try to run each generated app (just verify structure)
    print("\n" + "=" * 60)
    print("📦 Verifying Generated Code")

    for res in results:
        if res["success"] and res["file"]:
            run_generated_app(res["file"], res["lang"], res["hint"])

    # Summary
    print("\n" + "=" * 60)
    print("📊 T08 Test Summary")
    print("-" * 40)

    success_count = sum(1 for r in results if r["success"])
    print(f"✅ Successful: {success_count}/{len(results)}")

    for res in results:
        status = "✅" if res["success"] else "❌"
        print(f"{status} {res['description']}")
        if res["success"]:
            print(f"   → {res['lang']}: {res['file']}")

    if success_count == len(results):
        print("\n🎉 All T08 tests passed!")
        print("\n📝 Next Steps:")
        print("1. Run each generated app:")
        print("   python app.py")
        print("   PORT=8080 go run main.go")
        print("   cargo run")
        print("   PORT=5080 dotnet run")
        print("\n2. Commit changes:")
        print("   git add -A")
        print('   git commit -m "feat(T08): router wired + PORT-aware + /healthz"')
        return 0
    else:
        print(f"\n⚠️  Some tests failed ({len(results) - success_count}/{len(results)})")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
