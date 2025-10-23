#!/usr/bin/env python3
"""
Test Aurora-X English Command Understanding
"""

import subprocess
import sys


def test_english_command(command, expected_in_output):
    """Test an English command and check if expected output is present"""
    print(f"\n✨ Testing: '{command}'")
    result = subprocess.run(
        f'make say WHAT="{command}"', shell=True, capture_output=True, text=True
    )

    success = expected_in_output.lower() in result.stdout.lower()
    if success:
        print(f"  ✅ Success - Generated {expected_in_output}")
        # Extract the run directory
        lines = result.stdout.split("\n")
        for line in lines:
            if "v3 generated:" in line:
                run_dir = line.split("v3 generated:")[1].strip()
                print(f"     Generated code at: {run_dir}")
                break
    else:
        print(f"  ❌ Failed - Expected '{expected_in_output}' in output")
        print(f"     Output: {result.stdout[:200]}")

    return success


def main():
    print("=" * 60)
    print("Aurora-X English Command Understanding Test Suite")
    print("=" * 60)

    tests = [
        ("reverse a string", "reverse_string"),
        ("find the largest number in a list", "max_in_list"),
        ("calculate factorial", "factorial"),
        ("check if a string is palindrome", "is_palindrome"),
        ("add two numbers together", "add_two_numbers"),
        ("compute the fibonacci sequence", "fibonacci"),
        ("check if a number is prime", "is_prime"),
        ("sort a list of numbers", "sort_list"),
        ("count vowels in text", "count_vowels"),
        ("find the greatest common divisor", "gcd"),
    ]

    passed = 0
    failed = 0

    for command, expected in tests:
        if test_english_command(command, expected):
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
