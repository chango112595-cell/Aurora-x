
#!/usr/bin/env python3
"""Debug all backend-frontend connections"""

import requests
import json
import sys

def test_endpoint(name, method, url, data=None):
    """Test a single endpoint"""
    print(f"\n🔍 Testing {name}...")
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
        if response.status_code < 400:
            print(f"   ✅ {name} OK")
            return True
        else:
            print(f"   ❌ {name} FAILED")
            return False
    except Exception as e:
        print(f"   ❌ {name} ERROR: {e}")
        return False

def main():
    """Run all connection tests"""
    print("🌟 Aurora Connection Debug Tool")
    print("=" * 50)
    
    base_url = "http://0.0.0.0:5000"
    
    tests = [
        ("Health Check", "GET", f"{base_url}/healthz", None),
        ("API Health", "GET", f"{base_url}/api/health", None),
        ("Chat Endpoint", "POST", f"{base_url}/api/chat", {
            "message": "test connection",
            "session_id": "debug"
        }),
        ("Main Page", "GET", f"{base_url}/", None),
    ]
    
    results = []
    for test in tests:
        results.append(test_endpoint(*test))
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("✅ All connections working!")
        return 0
    else:
        print("⚠️  Some connections failed - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
