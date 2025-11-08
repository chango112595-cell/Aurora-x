#!/usr/bin/env python3
"""
Aurora's Self-Diagnostic for Chat System
Let Aurora figure out what's wrong!
"""

import subprocess

import requests

print("🌌 Aurora's Chat System Diagnostic")
print("=" * 60)

# Test 1: Backend conversation endpoint
print("\n1️⃣ Testing backend /api/conversation...")
try:
    response = requests.post(
        "http://localhost:5000/api/conversation", json={"message": "test", "session_id": "diagnostic"}, timeout=5
    )
    if response.status_code == 200:
        print(f"   ✅ Backend responds: {response.status_code}")
        print(f"   Response: {response.json().get('response', '')[:100]}...")
    else:
        print(f"   ❌ Backend error: {response.status_code}")
        print(f"   {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Backend unreachable: {e}")

# Test 2: Luminar Nexus chat endpoint
print("\n2️⃣ Testing Luminar Nexus /api/chat...")
try:
    response = requests.post(
        "http://localhost:5003/api/chat", json={"message": "test", "session_id": "diagnostic"}, timeout=5
    )
    if response.status_code == 200:
        print(f"   ✅ Luminar Nexus responds: {response.status_code}")
        print(f"   Response: {response.json().get('response', '')[:100]}...")
    else:
        print(f"   ❌ Luminar Nexus error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Luminar Nexus unreachable: {e}")

# Test 3: Vite proxy
print("\n3️⃣ Testing Vite frontend proxy...")
try:
    response = requests.post(
        "http://localhost:5173/api/conversation", json={"message": "test", "session_id": "diagnostic"}, timeout=5
    )
    if response.status_code == 200:
        print(f"   ✅ Vite proxy works: {response.status_code}")
        print(f"   Response: {response.json().get('response', '')[:100]}...")
    else:
        print(f"   ❌ Vite proxy error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Vite proxy unreachable: {e}")

# Test 4: Check tmux sessions
print("\n4️⃣ Checking service status...")
try:
    result = subprocess.run(["tmux", "list-sessions"], capture_output=True, text=True)
    sessions = result.stdout
    aurora_sessions = [s for s in sessions.split("\n") if "aurora" in s.lower()]
    print(f"   Found {len(aurora_sessions)} Aurora sessions:")
    for sess in aurora_sessions[:5]:
        print(f"   • {sess}")
except Exception as e:
    print(f"   ⚠️  Could not check tmux: {e}")

# Test 5: Check browser console logs (simulate)
print("\n5️⃣ Browser-side check (what would happen in browser)...")
print("   Expected flow:")
print("   1. User types message in chat UI")
print("   2. Frontend calls: fetch('/api/conversation', POST)")
print("   3. Vite dev server proxies to backend (5000)")
print("   4. Backend proxies to Luminar Nexus (5003)")
print("   5. Response flows back")

# Test 6: Check if there's a CORS issue
print("\n6️⃣ Testing CORS headers...")
try:
    response = requests.options("http://localhost:5173/api/conversation", headers={"Origin": "http://localhost:5173"})
    print(f"   OPTIONS preflight: {response.status_code}")
    print(f"   CORS headers: {dict(response.headers)}")
except Exception as e:
    print(f"   ⚠️  CORS check failed: {e}")

# Test 7: Check vite config for proxy
print("\n7️⃣ Checking Vite proxy configuration...")
try:
    with open("/workspaces/Aurora-x/vite.config.ts") as f:
        config = f.read()
        if "proxy" in config:
            print("   ✅ Vite proxy configuration found")
            # Extract proxy config
            proxy_section = config[config.find("proxy") : config.find("proxy") + 500]
            print(f"   {proxy_section[:300]}...")
        else:
            print("   ❌ No proxy configuration in vite.config.ts")
            print("   🔧 ISSUE FOUND: Vite needs proxy config!")
except Exception as e:
    print(f"   ⚠️  Could not read vite.config: {e}")

print("\n" + "=" * 60)
print("🧠 Aurora's Analysis:")
print("=" * 60)

# Aurora's diagnosis
print(
    """
Based on the tests above:

✅ If all backend tests pass → Issue is in frontend/browser
❌ If backend fails → Backend/Luminar Nexus connection broken
⚠️  If Vite proxy missing → Need to add proxy config to vite.config.ts

Most likely issue: Vite dev server doesn't proxy /api/* to backend!

🔧 FIX: Add to vite.config.ts:
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true
    }
  }
}
"""
)
