#!/usr/bin/env python3
"""
Test Aurora-X English synthesis - verify real code is generated
"""

import subprocess


def test_english_request(request_text):
    """Test that an English request generates real code, not todo_spec"""
    print(f"\n📝 Testing: '{request_text}'")

    # Generate spec from English
    from aurora_x.spec.parser_v2 import english_to_spec

    spec = english_to_spec(request_text)
    print(f"   ✓ Generated spec for: {spec.split('##')[0].strip()}")

    # Save spec to file
    spec_file = f"specs/test_{request_text[:20].replace(' ', '_')}.md"
    with open(spec_file, "w") as f:
        f.write(spec)

    # Run synthesis
    subprocess.run(f"python -m aurora_x.main --spec {spec_file}", shell=True, capture_output=True, text=True)

    # Find the generated run directory
    import glob

    runs = sorted(glob.glob("runs/run-*"))
    if runs:
        latest_run = runs[-1]
        src_files = glob.glob(f"{latest_run}/src/*.py")
        if src_files:
            with open(src_files[0]) as f:
                code = f.read()
                print(f"   ✓ Generated code in: {src_files[0]}")

                # Check it's not todo_spec
                if "todo_spec" in code:
                    print("   ❌ ERROR: Still generating todo_spec!")
                    return False
                elif "raise NotImplementedError" in code:
                    print("   ❌ ERROR: Still has NotImplementedError!")
                    return False
                else:
                    # Show first few lines of actual implementation
                    lines = code.split("\n")
                    for line in lines[1:6]:  # Skip header comment
                        if line.strip() and not line.startswith("#"):
                            print(f"      Code: {line.strip()[:60]}...")
                            break
                    print("   ✅ SUCCESS: Real code generated!")
                    return True

    print("   ⚠️  Could not find generated code")
    return False


# Test various English requests
test_cases = ["reverse a string", "add two numbers", "calculate factorial", "check if palindrome"]

print("=" * 60)
print("Aurora-X English Synthesis Test")
print("=" * 60)

passed = 0
failed = 0

for test in test_cases:
    if test_english_request(test):
        passed += 1
    else:
        failed += 1

print("\n" + "=" * 60)
print(f"Results: {passed} passed, {failed} failed")
print("=" * 60)

if failed == 0:
    print("\n🎉 All tests passed! Aurora-X is generating real code from English!")
else:
    print("\n⚠️  Some tests failed. Check the implementation.")
