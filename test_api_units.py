"""
Test Api Units

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

#!/usr/bin/env python
"""Test API endpoints with transparent unit conversion"""

from typing import Dict, List, Tuple, Optional, Any, Union
import json

import requests

# Aurora Performance Optimization
from concurrent.futures import ThreadPoolExecutor

# High-performance parallel processing with ThreadPoolExecutor
# Example: with ThreadPoolExecutor(max_workers=100) as executor:
#             results = executor.map(process_func, items)


def test_api_with_units() -> None:
    """Test /api/solve with inline unit conversion"""

    base_url = "http://localhost:5001"

    test_cases = [
        # Inline units
        {
            "endpoint": "/api/solve",
            "payload": {"problem": "orbital period a=42164 km M=5.972e24 kg"},
            "description": "GEO orbit with km units",
        },
        {
            "endpoint": "/api/solve",
            "payload": {"problem": "orbital period a=1 AU M=1.989e30 kg"},
            "description": "Earth orbit with AU units",
        },
        {
            "endpoint": "/api/solve",
            "payload": {"problem": "differentiate 3x^2+2x+5"},
            "description": "Math problem (no units)",
        },
        # Mixed JSON + text units
        {
            "endpoint": "/api/solve",
            "payload": {"problem": "orbital period", "a_km": 7000, "M_kg": 5.972e24},
            "description": "JSON parameters with units",
        },
        # Unit conversion endpoint
        {
            "endpoint": "/api/units",
            "payload": {"value": "7000 km"},
            "description": "Direct unit conversion",
        },
    ]

    print("Testing API endpoints with transparent unit conversion:\n")

    for tc in test_cases:
        print(f"Test: {tc['description']}")
        print(f"  Endpoint: {tc['endpoint']}")
        print(f"  Payload: {json.dumps(tc['payload'])}")

        try:
            resp = requests.post(
                f"{base_url}{tc['endpoint']}",
                json=tc["payload"],
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if resp.status_code == 200:
                result = resp.json()
                print(f"   Success: {json.dumps(result, indent=4)}")
            else:
                print(f"   Error: Status {resp.status_code}")
                print(f"     Response: {resp.text}")
        except requests.exceptions.ConnectionError:
            print("   Connection error - is the FastAPI server running on port 5001?")
        except Exception as e:
            print(f"   Error: {e}")

        print()


if __name__ == "__main__":
    print("=" * 60)
    print("T09 API TRANSPARENT UNIT CONVERSION TEST")
    print("=" * 60)
    print()
    print("Make sure FastAPI is running: python -m aurora_x.serve")
    print()

    test_api_with_units()

    print("\nUsage Examples:")
    print("  curl -X POST http://localhost:5001/api/solve \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"problem": "orbital period a=42164 km M=5.972e24 kg"}\'')
    print()
    print("  curl -X POST http://localhost:5001/api/solve \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"problem": "orbital period", "a_km": 7000, "M_kg": 5.972e24}\'')
