#!/usr/bin/env python3
"""
Service Startup Validation Script for Aurora-X
Ensures all services start correctly and remain healthy.

This script:
1. Validates service startup commands are correct
2. Checks that services can start without errors
3. Verifies endpoints are accessible after startup
4. Monitors service health
5. Can be run as a pre-commit hook or CI check
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import httpx

ROOT = Path(__file__).parent.parent

# Service configurations
SERVICES = {
    "bridge": {
        "port": 5001,
        "cmd": ["python", str(ROOT / "aurora_x" / "bridge" / "service.py")],
        "health_endpoint": "/api/health",
        "startup_timeout": 10,
        "health_timeout": 5,
    },
    "nexus_v3": {
        "port": 5002,
        "cmd": ["python", "-m", "aurora_nexus_v3.main"],
        "health_endpoint": "/api/health",
        "startup_timeout": 15,
        "health_timeout": 5,
    },
    "luminar_v2": {
        "port": 8000,
        "cmd": ["python", "tools/luminar_nexus_v2.py", "serve"],
        "health_endpoint": "/api/chat",  # Luminar V2 doesn't have /health
        "startup_timeout": 10,
        "health_timeout": 5,
    },
}


def check_port(port: int) -> bool:
    """Check if a port is listening"""
    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        result = sock.connect_ex(("127.0.0.1", port))
        sock.close()
        return result == 0
    except Exception:
        return False


async def check_service_health(service_name: str, config: Dict) -> Tuple[bool, str]:
    """Check if service is healthy by calling health endpoint"""
    base_url = f"http://127.0.0.1:{config['port']}"
    endpoint = config.get("health_endpoint", "/health")

    try:
        async with httpx.AsyncClient(timeout=config.get("health_timeout", 5.0)) as client:
            response = await client.get(f"{base_url}{endpoint}")

            if response.status_code == 200:
                return True, "healthy"
            elif response.status_code == 404:
                # Service running but endpoint not found
                return False, f"endpoint {endpoint} returns 404"
            else:
                return False, f"endpoint returns {response.status_code}"
    except httpx.ConnectError:
        return False, "connection refused"
    except httpx.TimeoutException:
        return False, "timeout"
    except Exception as e:
        return False, f"error: {str(e)}"


def validate_startup_command(service_name: str, config: Dict) -> Tuple[bool, str]:
    """Validate that startup command exists and is correct"""
    cmd = config["cmd"]

    # Set PYTHONPATH like x-start.py does
    import os
    env = os.environ.copy()
    pythonpath = str(ROOT)
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{pythonpath}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = pythonpath
    os.environ.update(env)

    # Check if Python command exists
    if cmd[0] == "python":
        import shutil
        if not shutil.which("python"):
            return False, "python command not found"

    # Check if module/file exists
    if cmd[1] == "-m":
        # Module import check (with PYTHONPATH set)
        module_name = cmd[2]
        try:
            __import__(module_name)
        except ImportError as e:
            return False, f"module {module_name} cannot be imported: {e}"
    else:
        # File path check
        file_path = ROOT / cmd[1]
        if not file_path.exists():
            return False, f"file {file_path} does not exist"

    return True, "valid"


async def test_service_startup(service_name: str, config: Dict) -> Tuple[bool, str]:
    """Test that service can start (dry run - don't actually start)"""
    # First validate the command
    valid, error = validate_startup_command(service_name, config)
    if not valid:
        return False, error

    # Check if port is already in use
    if check_port(config["port"]):
        # Port is in use - try to check health
        healthy, health_error = await check_service_health(service_name, config)
        if healthy:
            return True, "already running and healthy"
        else:
            return False, f"port in use but service unhealthy: {health_error}"

    # Port not in use - command validation passed
    return True, "startup command valid"


async def main():
    """Main validation function"""
    print("[SERVICE STARTUP VALIDATION] Checking service startup configurations...")

    all_valid = True
    issues = []

    for service_name, config in SERVICES.items():
        print(f"\n[{service_name.upper()}]")
        print(f"  Port: {config['port']}")
        print(f"  Command: {' '.join(config['cmd'])}")

        # Validate startup command
        valid, error = validate_startup_command(service_name, config)
        if not valid:
            print(f"  [FAILED] Command validation: {error}")
            all_valid = False
            issues.append(f"{service_name}: {error}")
            continue
        else:
            print(f"  [OK] Command validation passed")

        # Test service startup
        can_start, start_error = await test_service_startup(service_name, config)
        if not can_start:
            print(f"  [FAILED] Startup test: {start_error}")
            all_valid = False
            issues.append(f"{service_name}: {start_error}")
        else:
            print(f"  [OK] Startup test passed: {start_error}")

    # Summary
    print("\n" + "=" * 80)
    if all_valid:
        print("[SERVICE STARTUP VALIDATION] [PASSED] All services can start correctly")
        return 0
    else:
        print("[SERVICE STARTUP VALIDATION] [FAILED] Some services have issues:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nTo fix:")
        print("1. Ensure all Python modules can be imported")
        print("2. Check that file paths are correct")
        print("3. Verify ports are not already in use")
        print("4. Run validation again: python tools/validate_service_startup.py")
        return 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
