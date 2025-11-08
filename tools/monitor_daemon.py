#!/usr/bin/env python3
import subprocess
import time
from datetime import datetime

import requests


def monitor_services():
    """Continuous monitoring with auto-recovery"""
    services = {
        5000: "Main Aurora Web Server",
        5001: "Python Bridge",
        5002: "Self-Learning Server",
        8080: "File Server",
    }

    while True:
        print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - Health Check")

        for port, name in services.items():
            try:
                response = requests.get(f"http://localhost:{port}", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name} (:{port}): HEALTHY")
                else:
                    print(f"⚠️  {name} (:{port}): Status {response.status_code}")
            except Exception as e:
                print(f"❌ {name} (:{port}): DOWN - {str(e)[:50]}")
                # Auto-restart logic here
                if port == 5001:
                    subprocess.run(
                        ["python3", "tools/server_manager.py", "--restart-bridge"], cwd="/workspaces/Aurora-x"
                    )
                elif port == 5002:
                    subprocess.run(
                        ["python3", "tools/server_manager.py", "--restart-learning"], cwd="/workspaces/Aurora-x"
                    )

        time.sleep(30)  # Check every 30 seconds


if __name__ == "__main__":
    monitor_services()
