#!/usr/bin/env python3
"""
Test script for Flask synthesis
"""

import sys
import os
from pathlib import Path

# Add aurora_x to path
sys.path.insert(0, str(Path(__file__).parent))

from aurora_x.spec.parser_nl import parse_english
from aurora_x.templates.flask_app import generate_flask_app

# Test 1: Timer UI App
print("=" * 60)
print("Test 1: Timer UI Flask App")
print("=" * 60)

test_input = "Create a Flask web app with timer and dashboard UI"
parsed = parse_english(test_input)
print(f"\nParsed metadata:")
print(f"  Framework: {parsed.get('framework')}")
print(f"  Includes: {parsed.get('includes')}")
print(f"  Routes: {parsed.get('routes')}")

if parsed.get("framework") == "flask":
    flask_code = generate_flask_app(parsed)
    print(f"\nGenerated Flask app? {len(flask_code) > 0}")
    print(f"Code length: {len(flask_code)} characters")
    
    # Save to test file
    test_file = Path("test_timer_app.py")
    test_file.write_text(flask_code)
    print(f"Saved to: {test_file}")
    
    # Check key features
    print("\nKey features present:")
    print(f"  ✓ format_mmss function: {'format_mmss' in flask_code}")
    print(f"  ✓ create_app function: {'create_app' in flask_code}")
    print(f"  ✓ Timer HTML: {'timer-container' in flask_code}")
    print(f"  ✓ Aurora theme: {'aurora-primary' in flask_code}")
    print(f"  ✓ Unit tests: {'TestFormatMMSS' in flask_code}")
    port_check = 'port=port' in flask_code and "'5000'" in flask_code
    print(f"  ✓ Port 5000: {port_check}")

print("\n" + "=" * 60)
print("Test 2: API Flask App")
print("=" * 60)

test_input2 = "Create a Flask API with authentication endpoints"
parsed2 = parse_english(test_input2)
print(f"\nParsed metadata:")
print(f"  Framework: {parsed2.get('framework')}")
print(f"  Includes: {parsed2.get('includes')}")
print(f"  Routes: {parsed2.get('routes')}")

if parsed2.get("framework") == "flask":
    flask_code2 = generate_flask_app(parsed2)
    print(f"\nGenerated Flask API? {len(flask_code2) > 0}")
    print(f"Code length: {len(flask_code2)} characters")
    
    # Check API features
    print("\nAPI features present:")
    print(f"  ✓ Login endpoint: {'/api/auth/login' in flask_code2}")
    print(f"  ✓ Register endpoint: {'/api/auth/register' in flask_code2}")
    print(f"  ✓ CORS enabled: {'CORS' in flask_code2}")
    print(f"  ✓ JSON responses: {'jsonify' in flask_code2}")

print("\n✅ Flask synthesis template tests completed!")