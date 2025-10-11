#!/usr/bin/env python3
"""Test script for T09 Domain Router implementation"""

import json
from aurora_x.generators.solver import solve_text

def test_math_operations():
    """Test math operations (evaluation and differentiation)"""
    print("=" * 60)
    print("Testing Math Operations")
    print("=" * 60)
    
    # Test evaluation
    test_cases = [
        "2 + 3 * 4",
        "(2+3)**2 + 1",
        "3.14159 * 2**2"
    ]
    
    for expr in test_cases:
        result = solve_text(expr)
        print(f"\nExpression: {expr}")
        print(f"Result: {json.dumps(result, indent=2)}")
    
    # Test differentiation
    derivatives = [
        "differentiate 3x^2 + 2x + 5",
        "differentiate x^3 - 4x^2 + 2x - 7",
        "derivative of 5x^4 + 3x^2 + x"
    ]
    
    for expr in derivatives:
        result = solve_text(expr)
        print(f"\nDifferentiation: {expr}")
        print(f"Result: {json.dumps(result, indent=2)}")

def test_physics_operations():
    """Test physics operations (orbital period)"""
    print("\n" + "=" * 60)
    print("Testing Physics Operations")
    print("=" * 60)
    
    # Test orbital period
    physics_tests = [
        "orbital period a=7e6 M=5.972e24",
        "orbital period a=7000000 M=5.972e24",
        "calculate orbit period semi_major_axis_m=7e6 mass_central_kg=5.972e24"
    ]
    
    for test in physics_tests:
        result = solve_text(test)
        print(f"\nPhysics query: {test}")
        print(f"Result: {json.dumps(result, indent=2)}")
        if result.get("ok") and result.get("period_s"):
            period_hours = result["period_s"] / 3600
            print(f"Period in hours: {period_hours:.2f}")

def test_domain_classification():
    """Test domain classification"""
    print("\n" + "=" * 60)
    print("Testing Domain Classification")
    print("=" * 60)
    
    from aurora_x.router.domain_router import classify_domain
    
    test_inputs = [
        "calculate 5 + 10",
        "differentiate x^2",
        "orbital period of satellite",
        "electric field superposition",
        "write a python function to sort a list",
    ]
    
    for text in test_inputs:
        intent = classify_domain(text)
        print(f"\nInput: {text}")
        print(f"Domain: {intent.domain}, Task: {intent.task}")

if __name__ == "__main__":
    try:
        test_domain_classification()
        test_math_operations()
        test_physics_operations()
        print("\n" + "=" * 60)
        print("✅ All T09 tests completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()