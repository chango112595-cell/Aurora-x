#!/usr/bin/env python3
"""Simple test for the FastAPI /chat endpoint using uvicorn"""

import json
import os
import subprocess
import time

import requests


def test_chat_endpoint():
    """Test the /chat endpoint"""

    # Start the FastAPI server in background
    print("Starting FastAPI server...")
    server = subprocess.Popen(
        ["python", "-m", "uvicorn", "aurora_x.serve:app", "--port", "8000", "--host", "127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    time.sleep(3)

    try:
        # Test the /chat endpoint
        print("\nTesting /chat endpoint...")

        # Test 1: Valid web app prompt
        print("\n1. Testing web app prompt:")
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"prompt": "Build me a timer UI"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")

        # Test 2: CLI tool prompt
        print("\n2. Testing CLI tool prompt:")
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"prompt": "Make a CLI script"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")

        # Test 3: Empty prompt
        print("\n3. Testing empty prompt:")
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"prompt": ""}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")

        print("\n✅ All tests completed!")

        # Check if app.py was created
        if os.path.exists("app.py"):
            print("✅ app.py file was created successfully")
            with open("app.py") as f:
                lines = f.readlines()[:5]
                print("   First few lines of generated app.py:")
                for line in lines:
                    print(f"   {line.rstrip()}")

    finally:
        # Stop the server
        print("\nStopping server...")
        server.terminate()
        server.wait()

if __name__ == "__main__":
    test_chat_endpoint()
