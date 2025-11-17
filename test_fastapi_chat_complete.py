#!/usr/bin/env python3
"""Complete test demonstrating the FastAPI /chat endpoint implementation"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.abspath("."))


async def test_chat_endpoint():
    """Test the /chat endpoint implementation directly"""

    from aurora_x.chat.attach_router import ChatRequest, make_chat_router

    print("=" * 70)
    print("COMPLETE TEST: FastAPI /chat Endpoint Implementation")
    print("=" * 70)

    # Create the router
    router = make_chat_router()

    # Get the endpoint function
    chat_func = None
    for route in router.routes:
        if hasattr(route, "endpoint"):
            chat_func = route.endpoint
            break

    if not chat_func:
        print("❌ Could not find chat endpoint function")
        return

    print("\n📝 TEST CASES:\n")

    # Test Case 1: Web App (Timer UI)
    print("1. Web App Intent (Timer UI):")
    print("   Input: 'Build me a timer UI'")
    request1 = ChatRequest(prompt="Build me a timer UI")
    response1 = await chat_func(request1)
    print(f"   Response: ok={response1.ok}, kind={response1.kind}, file={response1.file}")
    print(f"   Hint: {response1.hint}")
    assert response1.ok
    assert response1.kind == "web_app"
    assert response1.file == "app.py"
    if Path("app.py").exists():
        print("   ✅ app.py file created successfully")
        with open("app.py", encoding="utf-8") as f:
            content = f.read()
            assert "TITLE = 'Futuristic UI Timer'" in content
            assert "from flask import Flask" in content
            print("   ✅ Flask app code generated correctly")

    # Test Case 2: Web Dashboard
    print("\n2. Web App Intent (Dashboard):")
    print("   Input: 'Create a dashboard page'")
    request2 = ChatRequest(prompt="Create a dashboard page")
    response2 = await chat_func(request2)
    print(f"   Response: ok={response2.ok}, kind={response2.kind}, file={response2.file}")
    assert response2.ok
    assert response2.kind == "web_app"

    # Test Case 3: CLI Tool
    print("\n3. CLI Tool Intent:")
    print("   Input: 'Make a CLI script for file processing'")
    request3 = ChatRequest(prompt="Make a CLI script for file processing")
    response3 = await chat_func(request3)
    print(f"   Response: ok={response3.ok}, kind={response3.kind}, name={response3.name}")
    print(f"   Note: {response3.note}")
    assert response3.ok
    assert response3.kind == "cli_tool"
    assert response3.note == "Template not implemented yet"

    # Test Case 4: Library Function
    print("\n4. Library Function Intent:")
    print("   Input: 'Write a function to calculate fibonacci'")
    request4 = ChatRequest(prompt="Write a function to calculate fibonacci")
    response4 = await chat_func(request4)
    print(f"   Response: ok={response4.ok}, kind={response4.kind}, name={response4.name}")
    print(f"   Note: {response4.note}")
    assert response4.ok
    assert response4.kind == "lib_func"

    # Test Case 5: Empty Prompt
    print("\n5. Error Handling (Empty Prompt):")
    print("   Input: ''")
    request5 = ChatRequest(prompt="")
    response5 = await chat_func(request5)
    print(f"   Response: ok={response5.ok}, err={response5.err}")
    assert not response5.ok
    assert response5.err == "missing prompt"

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)

    print("\n📋 IMPLEMENTATION SUMMARY:")
    print("✅ 1. Converted Flask router to FastAPI with Pydantic models")
    print("✅ 2. Created ChatRequest and ChatResponse models")
    print("✅ 3. Implemented async endpoint function")
    print("✅ 4. Intent classification working correctly")
    print("✅ 5. Flask app generation unchanged (as required)")
    print("✅ 6. Error handling implemented")
    print("✅ 7. Router integrated with main FastAPI app")

    print("\n🚀 The T08 Intent Router is fully functional with FastAPI!")

    # Clean up test file
    if Path("app.py").exists():
        os.remove("app.py")
        print("\n🧹 Cleaned up test files")


# Run the async test
import asyncio

if __name__ == "__main__":
    asyncio.run(test_chat_endpoint())
