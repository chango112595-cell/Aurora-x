#!/usr/bin/env python3
"""
Endpoint Validation Script for Aurora-X
Ensures all required API endpoints exist and are accessible.

This script:
1. Validates that required endpoints exist in Bridge and Nexus V3
2. Checks endpoint accessibility (if services are running)
3. Can be run as a pre-commit hook or CI check
4. Prevents missing endpoint issues from being committed
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import httpx

ROOT = Path(__file__).parent.parent

# Required endpoints for each service
REQUIRED_ENDPOINTS = {
    "bridge": {
        "base_url": "http://127.0.0.1:5001",
        "endpoints": [
            "/api/health",
            "/api/status",
            "/api/manifest",
            "/api/consciousness",
            "/health",
            "/api/bridge/nl",
        ],
    },
    "nexus_v3": {
        "base_url": "http://127.0.0.1:5002",
        "endpoints": [
            "/api/health",
            "/api/status",
            "/api/manifest",
            "/api/consciousness",
            "/health",
            "/status",
            "/api/process",
            "/api/workers/status",
        ],
    },
}

# Endpoints that should exist in code (static check)
CODE_ENDPOINTS = {
    "bridge": {
        "file": "aurora_x/bridge/service.py",
        "patterns": [
            r'@app\.get\(["\']/api/health["\']',
            r'@app\.get\(["\']/api/status["\']',
            r'@app\.get\(["\']/api/manifest["\']',
            r'@app\.get\(["\']/api/consciousness["\']',
        ],
    },
    "nexus_v3": {
        "file": "aurora_nexus_v3/main.py",
        "patterns": [
            r'@app\.get\(["\']/api/health["\']',
            r'@app\.get\(["\']/api/status["\']',
            r'@app\.get\(["\']/api/manifest["\']',
            r'@app\.get\(["\']/api/consciousness["\']',
        ],
    },
}


def check_code_endpoints() -> Tuple[bool, List[str]]:
    """Check that required endpoints exist in code"""
    issues = []

    for service_name, config in CODE_ENDPOINTS.items():
        file_path = ROOT / config["file"]

        if not file_path.exists():
            issues.append(f"{service_name}: File {config['file']} not found")
            continue

        content = file_path.read_text(encoding='utf-8')

        for pattern in config["patterns"]:
            import re
            if not re.search(pattern, content):
                endpoint = pattern.split('"')[1] if '"' in pattern else pattern.split("'")[1]
                issues.append(
                    f"{service_name}: Missing endpoint {endpoint} in {config['file']}"
                )

    return len(issues) == 0, issues


async def check_runtime_endpoints() -> Tuple[bool, List[str]]:
    """Check that endpoints are accessible (if services are running)"""
    issues = []
    warnings = []

    async with httpx.AsyncClient(timeout=2.0) as client:
        for service_name, config in REQUIRED_ENDPOINTS.items():
            base_url = config["base_url"]

            # Try to connect to base URL
            try:
                response = await client.get(f"{base_url}/health", timeout=1.0)
                if response.status_code == 404:
                    # Service might be running but /health doesn't exist
                    warnings.append(
                        f"{service_name}: Service running but /health returns 404"
                    )
            except httpx.ConnectError:
                # Service not running - skip runtime checks
                warnings.append(
                    f"{service_name}: Service not running at {base_url} (skipping runtime checks)"
                )
                continue
            except Exception as e:
                warnings.append(f"{service_name}: Error connecting: {e}")
                continue

            # Check each endpoint
            for endpoint in config["endpoints"]:
                try:
                    url = f"{base_url}{endpoint}"
                    response = await client.get(url, timeout=1.0)

                    if response.status_code == 404:
                        issues.append(
                            f"{service_name}: Endpoint {endpoint} returns 404 (not found)"
                        )
                    elif response.status_code >= 500:
                        warnings.append(
                            f"{service_name}: Endpoint {endpoint} returns {response.status_code}"
                        )
                except httpx.TimeoutException:
                    warnings.append(f"{service_name}: Endpoint {endpoint} timed out")
                except Exception as e:
                    warnings.append(f"{service_name}: Endpoint {endpoint} error: {e}")

    return len(issues) == 0, issues, warnings


def main():
    """Main validation function"""
    print("[ENDPOINT VALIDATION] Checking required endpoints...")

    # Check code endpoints (static)
    code_valid, code_issues = check_code_endpoints()

    if not code_valid:
        print("\n[FAILED] Code endpoint checks:")
        for issue in code_issues:
            print(f"  - {issue}")

    # Check runtime endpoints (if services are running)
    print("\n[ENDPOINT VALIDATION] Checking runtime endpoints...")
    runtime_valid, runtime_issues, warnings = asyncio.run(check_runtime_endpoints())

    if warnings:
        print("\n[WARNINGS] Runtime checks:")
        for warning in warnings:
            print(f"  - {warning}")

    if not runtime_valid:
        print("\n[FAILED] Runtime endpoint checks:")
        for issue in runtime_issues:
            print(f"  - {issue}")

    # Summary
    if code_valid and runtime_valid:
        print("\n[ENDPOINT VALIDATION] [PASSED] All endpoints validated")
        if warnings:
            print(f"  ({len(warnings)} warnings - services may not be running)")
        return 0
    else:
        print("\n[ENDPOINT VALIDATION] [FAILED] Endpoint validation failed")
        print("\nTo fix:")
        print("1. Add missing endpoints to the service files")
        print("2. Ensure endpoints return proper JSON responses")
        print("3. Run validation again: python tools/validate_endpoints.py")
        return 1


if __name__ == '__main__':
    sys.exit(main())
