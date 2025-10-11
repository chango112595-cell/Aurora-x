#!/usr/bin/env python3
"""
T09 Domain Router - Working Example
Demonstrates real calls to math/physics solvers
"""

from aurora_x.generators.solver import solve_text

def custom_function():
    examples = {
        "math_eval": "2 + 3 * 4",
        "math_diff": "differentiate x^3 - 2x^2 + x",
        "phys_leo": "orbital period a=7e6 M=5.972e24",
        "phys_geo": "orbital period a=4.22e7 M=5.972e24",
    }
    return {k: solve_text(v) for k, v in examples.items()}

if __name__ == "__main__":
    import json
    print(json.dumps(custom_function(), indent=2))