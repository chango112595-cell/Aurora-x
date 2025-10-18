#!/usr/bin/env python3
"""
Test the T08 Intent Router and chat endpoint locally
"""
from pathlib import Path

from aurora_x.router.intent_router import classify
from aurora_x.templates.web_app_flask import render_app


def test_chat_endpoint(prompt):
    """Simulate what the /chat endpoint does"""
    print(f"\n🔍 Testing prompt: {prompt}")

    # Classify intent
    intent = classify(prompt)
    print(f"📋 Classified as: {intent.kind} (name: {intent.name})")

    # Handle web_app intent
    if intent.kind == "web_app":
        title = "Futuristic UI Timer" if intent.fields.get("feature")=="timer" else intent.name.replace('_',' ').title()
        code = render_app(title=title, subtitle=intent.brief)

        # Save the generated Flask app
        output_file = Path("generated_timer_app.py")
        output_file.write_text(code, encoding="utf-8")

        result = {
            "ok": True,
            "kind": "web_app",
            "file": str(output_file),
            "hint": "Run: python generated_timer_app.py",
            "code_length": len(code)
        }
        print(f"✅ Generated Flask app: {output_file}")
        print(f"📊 Code length: {len(code)} chars")
        print(f"💡 Hint: {result['hint']}")
        return result

    # Other intents not yet implemented
    result = {
        "ok": True,
        "kind": intent.kind,
        "name": intent.name,
        "note": f"Template for {intent.kind} not implemented yet"
    }
    print(f"⚠️  {result['note']}")
    return result

# Test cases
test_prompts = [
    "make a futuristic timer ui",
    "create a countdown timer with neon effects",
    "build a web dashboard",
    "create a CLI tool to hash files",
    "write factorial(n) with tests"
]

print("=" * 60)
print("T08 Intent Router Test Suite")
print("=" * 60)

for prompt in test_prompts:
    result = test_chat_endpoint(prompt)

print("\n" + "=" * 60)
print("✅ Test complete!")

# Verify the generated app exists
if Path("generated_timer_app.py").exists():
    print("\n📁 Generated file exists: generated_timer_app.py")
    print("🚀 You can run: python generated_timer_app.py")
    print("   Then open: http://localhost:5000")
