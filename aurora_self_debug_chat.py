#!/usr/bin/env python3
"""
Aurora Self-Debug: Chat Response Hanging Issue
Aurora debugging herself to find why chat is stuck on "generating"
"""

import subprocess
import time

import requests

print("🔍 Aurora Self-Diagnostic: Chat Hanging Issue")
print("=" * 60)

# Test 1: Check if Luminar Nexus chat service is responding
print("\n1️⃣ Testing Luminar Nexus chat endpoint...")
try:
    start_time = time.time()
    response = requests.post(
        "http://localhost:5003/api/chat", json={"message": "test", "session_id": "debug"}, timeout=5
    )
    elapsed = time.time() - start_time
    print(f"   ✅ Response received in {elapsed:.2f}s")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response preview: {response.json()['response'][:100]}...")
except requests.exceptions.Timeout:
    print("   ❌ TIMEOUT: Luminar Nexus not responding within 5s")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 2: Check backend proxy endpoint
print("\n2️⃣ Testing backend /api/conversation endpoint...")
try:
    start_time = time.time()
    response = requests.post(
        "http://localhost:5000/api/conversation", json={"message": "test", "session_id": "debug"}, timeout=5
    )
    elapsed = time.time() - start_time
    print(f"   ✅ Response received in {elapsed:.2f}s")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
except requests.exceptions.Timeout:
    print("   ❌ TIMEOUT: Backend not responding within 5s")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 3: Check tmux sessions
print("\n3️⃣ Checking tmux sessions...")
try:
    result = subprocess.run(["tmux", "list-sessions"], capture_output=True, text=True, check=False, check=False)
    sessions = result.stdout.strip().split("\n")
    aurora_sessions = [s for s in sessions if "aurora" in s.lower()]
    for session in aurora_sessions:
        print(f"   📋 {session}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 4: Check chat service logs
print("\n4️⃣ Checking chat service logs...")
try:
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", "aurora-chat", "-p", "-S", "-20"], capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        print("   Last 20 lines from chat service:")
        print("   " + "\n   ".join(result.stdout.strip().split("\n")[-10:]))
    else:
        print("   ❌ Chat session not found or not accessible")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 5: Check backend logs
print("\n5️⃣ Checking backend logs...")
try:
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", "aurora-backend", "-p", "-S", "-20"], capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        print("   Last 20 lines from backend:")
        print("   " + "\n   ".join(result.stdout.strip().split("\n")[-10:]))
    else:
        print("   ❌ Backend session not found")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 6: Check for port conflicts
print("\n6️⃣ Checking for port conflicts...")
try:
    result = subprocess.run(["lsof", "-i", ":5003"], capture_output=True, text=True, check=False, check=False)
    if result.stdout:
        lines = result.stdout.strip().split("\n")
        print(f"   Port 5003 processes: {len(lines) - 1}")
        for line in lines[:5]:
            print(f"   {line}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 60)
print("🤖 Aurora's Analysis:")
print("   If Luminar Nexus responds quickly but frontend hangs,")
print("   the issue is likely in the frontend JavaScript or")
print("   the backend proxy not returning the response properly.")
print("   If Luminar Nexus is slow, the issue is in process_message().")
print("=" * 60)
