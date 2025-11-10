#!/usr/bin/env python3
"""
Test script for Aurora health check and monitoring APIs
"""

import sys
import time

import psutil
import requests


def test_health_endpoints():
    """Test all health check and monitoring endpoints."""
    base_url = "http://localhost:5001"

    print("🧪 Aurora Monitoring & Health Check API Tests")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Basic health check
    print("\n1. Testing basic health check endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   ✅ Service: {data.get('service')}")
            tests_passed += 1
        else:
            print(f"   ❌ Failed with status code: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1

    # Test 2: Detailed health check
    print("\n2. Testing detailed health check endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health/detailed", timeout=5)
        if response.status_code in [200, 503]:  # 503 is also valid if something is degraded
            data = response.json()
            print(f"   ✅ Overall Status: {data.get('status')}")
            checks = data.get("checks", {})
            print(f"   ✅ CPU Status: {checks.get('cpu', {}).get('status')}")
            print(f"   ✅ Memory Status: {checks.get('memory', {}).get('status')}")
            print(f"   ✅ Disk Status: {checks.get('disk', {}).get('status')}")
            tests_passed += 1
        else:
            print(f"   ❌ Failed with status code: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1

    # Test 3: Liveness probe
    print("\n3. Testing liveness probe...")
    try:
        response = requests.get(f"{base_url}/api/health/liveness", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            tests_passed += 1
        else:
            print(f"   ❌ Failed with status code: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1

    # Test 4: Readiness probe
    print("\n4. Testing readiness probe...")
    try:
        response = requests.get(f"{base_url}/api/health/readiness", timeout=5)
        if response.status_code in [200, 503]:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            tests_passed += 1
        else:
            print(f"   ❌ Failed with status code: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1

    # Test 5: Metrics endpoint
    print("\n5. Testing metrics endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health/metrics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            metrics = data.get("metrics", {})
            print(f"   ✅ CPU: {metrics.get('cpu_percent')}%")
            print(f"   ✅ Memory: {metrics.get('memory_used_percent')}%")
            print(f"   ✅ Disk: {metrics.get('disk_used_percent')}%")
            tests_passed += 1
        else:
            print(f"   ❌ Failed with status code: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1

    # Test 6: Monitoring dashboard data
    print("\n6. Testing monitoring dashboard endpoint...")
    try:
        response = requests.get(f"{base_url}/api/monitoring/dashboard", timeout=5)
        if response.status_code == 200:
            data = response.json()
            overview = data.get("overview", {})
            print(f"   ✅ Services Running: {overview.get('services_running')}/{overview.get('services_total')}")
            print(f"   ✅ System Status: {overview.get('system_status')}")
            tests_passed += 1
        else:
            print(f"   ❌ Failed with status code: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1

    # Test 7: Alerts endpoint
    print("\n7. Testing alerts endpoint...")
    try:
        response = requests.get(f"{base_url}/api/monitoring/alerts", timeout=5)
        if response.status_code == 200:
            data = response.json()
            alert_count = data.get("count", 0)
            print(f"   ✅ Active Alerts: {alert_count}")
            if alert_count > 0:
                for alert in data.get("alerts", []):
                    print(f"      ⚠️  {alert.get('severity').upper()}: {alert.get('message')}")
            tests_passed += 1
        else:
            print(f"   ❌ Failed with status code: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1

    # Test 8: System status endpoint
    print("\n8. Testing system status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/monitoring/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Overall Status: {data.get('status')}")
            components = data.get("components", {})
            print(f"   ✅ Components: CPU={components.get('cpu')}, Memory={components.get('memory')}, Disk={components.get('disk')}")
            tests_passed += 1
        else:
            print(f"   ❌ Failed with status code: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        tests_failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Summary: {tests_passed}/{tests_passed + tests_failed} tests passed")
    if tests_failed == 0:
        print("✅ All monitoring and health check endpoints are working!")
        return 0
    else:
        print(f"❌ {tests_failed} tests failed")
        return 1


if __name__ == "__main__":
    # Check if server is running
    try:
        requests.get("http://localhost:5001/api/health/", timeout=2)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Backend server is not running on port 5001")
        print("   Start it with: uvicorn aurora_x.serve:app --host 0.0.0.0 --port 5001")
        sys.exit(1)

    sys.exit(test_health_endpoints())
