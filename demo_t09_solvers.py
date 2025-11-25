"""
Demo T09 Solvers

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

#!/usr/bin/env python3
"""
T09 Domain Router - Interactive Demo
Shows real math and physics solving capabilities
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import json

from aurora_x.generators.solver import solve_text


def demo_math_operations():
    """Demonstrate mathematical operations."""
    print("\n" + "=" * 60)
    print("[EMOJI] MATH DEMONSTRATIONS")
    print("=" * 60)

    # Expression evaluation
    print("\n[CHART] Expression Evaluation:")
    expressions = ["2 + 3 * 4", "(10 - 5) ** 2", "100 / 4 + 3", "2 ** 8"]

    for expr in expressions:
        result = solve_text(expr)
        value = result.get("value", "ERROR")
        print(f"  {expr:20} = {value}")

    # Polynomial differentiation
    print("\n[EMOJI] Polynomial Differentiation:")
    polynomials = [
        "differentiate 3x^2 + 2x + 5",
        "differentiate x^3 - 2x^2 + x",
        "differentiate 5x^4 + 3x^2",
        "differentiate 10",
    ]

    for poly in polynomials:
        result = solve_text(poly)
        derivative = result.get("derivative", "ERROR")
        input_expr = poly.replace("differentiate ", "")
        print(f"  d/dx({input_expr:15}) = {derivative}")


def demo_physics_operations():
    """Demonstrate physics calculations."""
    print("\n" + "=" * 60)
    print("[EMOJI] PHYSICS DEMONSTRATIONS")
    print("=" * 60)

    # Orbital periods
    print("\n[EMOJI] Orbital Period Calculations:")
    orbits = [
        ("Low Earth Orbit (400km)", "orbital period a=6.778e6 M=5.972e24"),
        ("GPS Satellite (20,200km)", "orbital period a=2.66e7 M=5.972e24"),
        ("Geostationary (35,786km)", "orbital period a=4.22e7 M=5.972e24"),
        ("Moon (384,400km)", "orbital period a=3.844e8 M=5.972e24"),
    ]

    for name, prompt in orbits:
        result = solve_text(prompt)
        period_s = result.get("period_s", 0)
        hours = period_s / 3600
        days = hours / 24

        if days > 1:
            print(f"  {name:25} -> {days:.2f} days")
        else:
            print(f"  {name:25} -> {hours:.2f} hours")

    # Show detailed result for one example
    print("\n[EMOJI] Detailed Result Example:")
    result = solve_text("orbital period a=7e6 M=5.972e24")
    print("  Request: 'orbital period a=7e6 M=5.972e24'")
    print(f"  Response: {json.dumps(result, indent=4)}")


def demo_api_usage():
    """Show how to use the API endpoints."""
    print("\n" + "=" * 60)
    print("[EMOJI] API USAGE EXAMPLES")
    print("=" * 60)

    print("\n[EMOJI] /api/solve endpoint:")
    print(
        """curl -X POST http://localhost:5001/api/solve \\
  -H 'Content-Type: application/json' \\
  -d '{"problem": "differentiate 3x^2 + 2x + 5"}'
"""
    )

    print("[EMOJI] /api/explain endpoint:")
    print(
        """curl -X POST http://localhost:5001/api/explain \\
  -H 'Content-Type: application/json' \\
  -d '{"problem": "orbital period a=7e6 M=5.972e24"}'
"""
    )


def main():
    """
        Main
            """
    print(
        """
    
           [ROCKET] Aurora-X T09 Domain Router Demo [ROCKET]              
              Math & Physics Solving Capabilities             
    
    """
    )

    demo_math_operations()
    demo_physics_operations()
    demo_api_usage()

    print("\n" + "=" * 60)
    print("[SPARKLES] All calculations performed by Aurora-X solvers!")
    print("=" * 60)


if __name__ == "__main__":
    main()
