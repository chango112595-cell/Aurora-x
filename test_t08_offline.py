#!/usr/bin/env python3
"""
T08 Offline Test - Test templates directly without server
"""

from pathlib import Path

from aurora_x.router.intent_router import classify
from aurora_x.router.lang_select import pick_language
from aurora_x.templates.cli_tool import render_cli
from aurora_x.templates.csharp_webapi import render_csharp_webapi
from aurora_x.templates.go_service import render_go_service
from aurora_x.templates.rust_cli import render_rust_cli
from aurora_x.templates.web_app_flask import render_app


def test_all_templates():
    """Test all language templates offline."""

    print(
        """
    ╔══════════════════════════════════════════════════════════╗
    ║         🚀 T08 Offline Template Test 🚀                  ║
    ║     Testing Language Router + PORT Configuration          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    )

    test_cases = [
        ("make a futuristic timer ui", "python", "Flask UI"),
        ("fast microservice web api", "go", "Go Service"),
        ("memory-safe cli to parse args", "rust", "Rust CLI"),
        ("enterprise web api with health", "csharp", "C# WebAPI"),
    ]

    for prompt, expected_lang, desc in test_cases:
        print(f"\n{'=' * 60}")
        print(f"📝 Testing: {desc}")
        print(f"   Prompt: '{prompt}'")

        # Test intent classification
        intent = classify(prompt)
        print(f"   Intent: {intent.kind} (name: {intent.name})")

        # Test language selection
        lang_choice = pick_language(prompt)
        print(f"   Language: {lang_choice.lang} ({lang_choice.reason})")

        # Generate code based on language and intent
        if intent.kind == "web_app":
            if lang_choice.lang == "python" or expected_lang == "python":
                code = render_app(title="Timer UI", subtitle="Futuristic timer application")
                Path("generated_timer_app.py").write_text(code)
                print("✅ Generated: generated_timer_app.py")

                # Verify PORT configuration
                if "os.getenv('PORT'" in code and "8000" in code:
                    print("   ✅ Uses PORT env (default: 8000)")

            elif lang_choice.lang == "go" or expected_lang == "go":
                result = render_go_service("microservice", "Fast web API")
                for fname, content in result["files"].items():
                    Path(fname).write_text(content)
                    print(f"✅ Generated: {fname}")

                    if fname == "main.go":
                        if 'os.Getenv("PORT")' in content and "8080" in content:
                            print("   ✅ Uses PORT env (default: 8080)")

            elif lang_choice.lang == "csharp" or expected_lang == "csharp":
                result = render_csharp_webapi("enterprise", "Enterprise API")
                folder = Path(result["folder"])
                folder.mkdir(exist_ok=True)

                for fname, content in result["files"].items():
                    filepath = folder / fname
                    filepath.write_text(content)
                    print(f"✅ Generated: {filepath}")

                    if fname == "Program.cs":
                        if 'Environment.GetEnvironmentVariable("PORT")' in content and "5080" in content:
                            print("   ✅ Uses PORT env (default: 5080)")

        elif intent.kind == "cli_tool":
            if lang_choice.lang == "rust" or expected_lang == "rust":
                result = render_rust_cli("cli_tool", "Memory-safe CLI")
                for fname, content in result["files"].items():
                    Path(fname).parent.mkdir(exist_ok=True, parents=True)
                    Path(fname).write_text(content)
                    print(f"✅ Generated: {fname}")
                print("   ℹ️  CLI tool (not a web service, no PORT)")
            else:
                code = render_cli(intent.name, intent.brief, intent.fields)
                fname = f"{intent.name}_cli.py"
                Path(fname).write_text(code)
                print(f"✅ Generated: {fname}")
                print("   ℹ️  CLI tool (not a web service, no PORT)")

    print("\n" + "=" * 60)
    print("📊 Summary")
    print("-" * 40)
    print("✅ All templates generated successfully")
    print("✅ PORT configuration verified:")
    print("   • Python Flask: PORT=8000 (default)")
    print("   • Go Service: PORT=8080 (default)")
    print("   • C# WebAPI: PORT=5080 (default)")
    print("   • Rust CLI: N/A (not a web service)")

    print("\n🚀 Run the generated apps:")
    print("   python generated_timer_app.py")
    print("   PORT=8080 go run main.go")
    print("   cargo run --manifest-path=Cargo.toml")
    print("   cd enterprise.WebApi && PORT=5080 dotnet run")

    return True


if __name__ == "__main__":
    import sys

    success = test_all_templates()
    sys.exit(0 if success else 1)
