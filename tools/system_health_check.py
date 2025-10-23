#!/usr/bin/env python3
"""Aurora-X System Health Check."""
import subprocess
import sys
from pathlib import Path


def check_python_deps():
    """Check Python dependencies."""
    try:
        import fastapi
        import pytest
        import uvicorn

        print("✅ Core Python dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False


def check_node_deps():
    """Check Node dependencies."""
    result = subprocess.run(["npm", "list"], capture_output=True)
    if result.returncode == 0:
        print("✅ Node dependencies installed")
        return True
    else:
        print("⚠️  Node dependencies may have issues")
        return False


def check_ports():
    """Check if required ports are available."""
    import socket

    ports = [5000, 5001]
    all_good = True

    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("0.0.0.0", port))
            sock.close()
            print(f"✅ Port {port} available")
        except OSError:
            print(f"⚠️  Port {port} in use")
            all_good = False

    return all_good


def check_directories():
    """Check required directories exist."""
    required = ["aurora_x", "runs", "specs", "tools", "data"]
    all_exist = True

    for dir_name in required:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/ exists")
        else:
            print(f"❌ {dir_name}/ missing")
            all_exist = False

    return all_exist


def main():
    """Run all health checks."""
    print("🏥 Aurora-X System Health Check")
    print("=" * 40)

    checks = [
        ("Python Dependencies", check_python_deps),
        ("Node Dependencies", check_node_deps),
        ("Required Directories", check_directories),
        ("Port Availability", check_ports),
    ]

    results = []
    for name, check_fn in checks:
        print(f"\n{name}:")
        results.append(check_fn())

    print("\n" + "=" * 40)
    if all(results):
        print("✅ All health checks passed")
        return 0
    else:
        print("❌ Some health checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
