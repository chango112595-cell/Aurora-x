#!/usr/bin/env python3
"""
Test script for T09 API endpoints
Run this after starting the FastAPI server with:
  uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5001
"""

import json

import requests

BASE_URL = "http://localhost:5001"

def test_api_endpoints():
    print("Testing T09 API Endpoints")
    print("=" * 60)

    # Test math differentiation
    print("\n1. Testing Math Differentiation:")
    response = requests.post(
        f"{BASE_URL}/api/solve",
        json={"problem": "differentiate 3x^2 + 2x + 5"}
    )
    print("   Request: differentiate 3x^2 + 2x + 5")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    # Test math evaluation
    print("\n2. Testing Math Evaluation:")
    response = requests.post(
        f"{BASE_URL}/api/solve",
        json={"problem": "2 + 3 * 4"}
    )
    print("   Request: 2 + 3 * 4")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    # Test physics orbital period
    print("\n3. Testing Physics Orbital Period:")
    response = requests.post(
        f"{BASE_URL}/api/solve",
        json={"prompt": "orbital period a=7e6 M=5.972e24"}
    )
    print("   Request: orbital period a=7e6 M=5.972e24")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    # Test explain endpoint
    print("\n4. Testing Explain Endpoint:")
    response = requests.post(
        f"{BASE_URL}/api/explain",
        json={"problem": "differentiate x^3"}
    )
    print("   Request: differentiate x^3")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")

    print("\n" + "=" * 60)
    print("✅ API endpoint tests completed!")

if __name__ == "__main__":
    try:
        test_api_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Connection error! Make sure the FastAPI server is running:")
        print("   uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5001")
    except Exception as e:
        print(f"❌ Error: {e}")
