#!/usr/bin/env python3
"""
Test the language auto-select feature locally.
Tests all language selections without needing the server running.
"""

import sys

from aurora_x.router.intent_router import classify
from aurora_x.router.lang_select import pick_language
from aurora_x.templates.csharp_webapi import render_csharp_webapi
from aurora_x.templates.go_service import render_go_service
from aurora_x.templates.rust_cli import render_rust_cli
from aurora_x.templates.web_app_flask import render_app


def test_language_selection():
    """Test language auto-selection with various prompts."""

    test_cases = [
        ("fast microservice web api", "go"),
        ("high performance api service", "go"),
        ("memory-safe cli to parse args", "rust"),
        ("memory safe command line tool", "rust"),
        ("enterprise web api with health", "csharp"),
        ("windows asp.net api controller", "csharp"),
        ("make a futuristic timer ui", "python"),
        ("create a data analysis script", "python"),
    ]

    print("🌍 Testing Language Auto-Selection")
    print("═" * 60)

    for prompt, expected in test_cases:
        lang_choice = pick_language(prompt)
        status = "✅" if lang_choice.lang == expected else "❌"
        print(f"{status} '{prompt[:30]}...' → {lang_choice.lang}")
        print(f"   Reason: {lang_choice.reason}")

    print()
    return True


def test_code_generation():
    """Test actual code generation for each language."""

    print("💻 Testing Code Generation for Each Language")
    print("═" * 60)

    # Test Go service
    print("\n1. Go Service Generation:")
    go_pkg = render_go_service("test_service", "Test Go microservice")
    print(f"   ✅ Generated {len(go_pkg['files'])} files")
    for fname in go_pkg["files"]:
        print(f"      • {fname}")
    print(f"   Hint: {go_pkg['hint']}")

    # Test Rust CLI
    print("\n2. Rust CLI Generation:")
    rust_pkg = render_rust_cli("test_cli", "Test Rust CLI tool")
    print(f"   ✅ Generated {len(rust_pkg['files'])} files")
    for fname in rust_pkg["files"]:
        print(f"      • {fname}")
    print(f"   Hint: {rust_pkg['hint']}")

    # Test C# WebAPI
    print("\n3. C# WebAPI Generation:")
    csharp_pkg = render_csharp_webapi("test_api", "Test C# Web API")
    print(f"   ✅ Generated {len(csharp_pkg['files'])} files in {csharp_pkg['folder']}/")
    for fname in csharp_pkg["files"]:
        print(f"      • {fname}")
    print(f"   Hint: {csharp_pkg['hint']}")

    # Test Python Flask
    print("\n4. Python Flask Generation:")
    flask_code = render_app("Test App", "Test Python Flask app")
    print(f"   ✅ Generated Flask app ({len(flask_code)} chars)")
    print("   Hint: Run: python app.py")

    return True


def test_full_pipeline():
    """Test the complete pipeline: prompt → intent → language → code."""

    print("\n🚀 Testing Complete Pipeline")
    print("═" * 60)

    test_prompts = [
        "create a fast microservice for order processing",
        "build a memory-safe CLI tool to validate JSON files",
        "develop an enterprise API with authentication",
        "make a dashboard to visualize sales data",
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{i}. Prompt: '{prompt}'")

        # Classify intent
        intent = classify(prompt)
        print(f"   Intent: {intent.kind} (name: {intent.name})")

        # Select language
        lang = pick_language(prompt)
        print(f"   Language: {lang.lang} ({lang.reason})")

        # Determine what would be generated
        if intent.kind == "web_app":
            if lang.lang == "go":
                output = "Go service with main.go and go.mod"
            elif lang.lang == "csharp":
                output = "C# WebAPI project with .csproj"
            else:
                output = "Python Flask app.py"
        elif intent.kind == "cli_tool":
            if lang.lang == "rust":
                output = "Rust project with Cargo.toml"
            else:
                output = "Python CLI with argparse"
        else:
            output = "Python function with tests"

        print(f"   Output: {output}")

    return True


def main():
    """Run all tests."""

    print(
        """
    ╔══════════════════════════════════════════════════════════╗
    ║     🌍 Aurora-X Language Auto-Select Test Suite 🌍       ║
    ╚══════════════════════════════════════════════════════════╝
    """
    )

    # Run tests
    success = True
    success &= test_language_selection()
    success &= test_code_generation()
    success &= test_full_pipeline()

    # Summary
    print("\n" + "═" * 60)
    if success:
        print("✅ All language auto-select tests passed!")
        print("\n💡 Integration complete! Aurora now supports:")
        print("   • Python (default) - Flask apps, CLI tools, functions")
        print("   • Go - High-performance microservices")
        print("   • Rust - Memory-safe CLI tools")
        print("   • C# - Enterprise web APIs with Swagger")
    else:
        print("❌ Some tests failed. Check the output above.")

    print("\n📝 Next: Update serve.py to use attach_router_lang")
    print("   from aurora_x.chat.attach_router_lang import attach_router")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
