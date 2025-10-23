#!/usr/bin/env python3
"""Test script for the FastAPI /chat endpoint"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient

from aurora_x.serve import app


def test_chat_endpoint():
    """Test the /chat endpoint with various prompts"""
    client = TestClient(app)

    print("Testing FastAPI /chat endpoint...")
    print("-" * 50)

    # Test 1: Valid web app prompt
    test_cases = [
        {"prompt": "Build me a timer UI", "expected_kind": "web_app", "expected_file": "app.py"},
        {
            "prompt": "Create a dashboard page",
            "expected_kind": "web_app",
            "expected_file": "app.py",
        },
        {
            "prompt": "Make a CLI tool for file processing",
            "expected_kind": "cli_tool",
            "expected_note": "Template not implemented yet",
        },
        {
            "prompt": "Write a function to calculate fibonacci",
            "expected_kind": "lib_func",
            "expected_note": "Template not implemented yet",
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['prompt']}")
        response = client.post("/chat", json={"prompt": test["prompt"]})

        # Check status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        print(f"  Response: {json.dumps(data, indent=2)}")

        # Validate response structure
        assert data["ok"], "Response should have ok=True"
        assert data["kind"] == test["expected_kind"], (
            f"Expected kind={test['expected_kind']}, got {data['kind']}"
        )

        if "expected_file" in test:
            assert data.get("file") == test["expected_file"], (
                f"Expected file={test['expected_file']}, got {data.get('file')}"
            )
            # Check if file was created for web_app
            if test["expected_kind"] == "web_app":
                assert os.path.exists("app.py"), "app.py should be created"
                print("  ✅ File app.py created successfully")

        if "expected_note" in test:
            assert data.get("note") == test["expected_note"], (
                f"Expected note={test['expected_note']}, got {data.get('note')}"
            )

    # Test empty prompt
    print(f"\nTest {len(test_cases) + 1}: Empty prompt")
    response = client.post("/chat", json={"prompt": ""})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    print(f"  Response: {json.dumps(data, indent=2)}")
    assert not data["ok"], "Empty prompt should return ok=False"
    assert data.get("err") == "missing prompt", "Should have error message for missing prompt"

    print("\n" + "=" * 50)
    print("✅ All tests passed successfully!")
    print("The FastAPI /chat endpoint is working correctly.")


if __name__ == "__main__":
    test_chat_endpoint()
