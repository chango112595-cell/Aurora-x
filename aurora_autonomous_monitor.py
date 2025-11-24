#!/usr/bin/env python3
"""
Aurora Autonomous System Monitor
Continuously monitors all services and auto-restarts them if they fail.
This ensures Aurora maintains 100% uptime autonomously.
"""

import platform
import socket
import subprocess
import time
from datetime import datetime

# Service configuration
SERVICES = {
    5000: {"name": "Backend API", "critical": True},
    5001: {"name": "Bridge Service", "critical": False},
    5002: {"name": "Self-Learning", "critical": False},
    5003: {"name": "Chat Server", "critical": True},
    5005: {"name": "Luminar Nexus", "critical": True},
    5173: {"name": "Frontend", "critical": True},
}


def check_port(port):
    """Check if a port is listening"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(("127.0.0.1", port))
        sock.close()
        return result == 0
    except Exception:
        return False


def restart_services():
    """Restart all Aurora services"""
    print(f"\n[RESTART] [{datetime.now().strftime('%H:%M:%S')}] Restarting Aurora services...")
    python_cmd = "python" if platform.system() == "Windows" else "python3"

    try:
        if platform.system() == "Windows":
            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "/min",
                    "powershell",
                    "-Command",
                    f"{python_cmd} tools\\luminar_nexus_v2.py serve",
                ],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            )
        else:
            subprocess.Popen(
                [python_cmd, "tools/luminar_nexus_v2.py", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        print("   [OK] Restart command issued")
        return True
    except Exception as e:
        print(f"   [ERROR] Restart failed: {e}")
        return False


def monitor_loop():
    """Main monitoring loop"""
    print("[MONITOR] Aurora Autonomous Monitor starting...")
    print("   Monitoring all services for failures")
    print("   Will auto-restart if critical services fail\n")

    failure_count = {}
    last_restart = 0

    while True:
        try:
            current_time = time.time()
            critical_failures = []

            for port, config in SERVICES.items():
                is_up = check_port(port)

                if not is_up:
                    failure_count[port] = failure_count.get(port, 0) + 1
                    if config["critical"]:
                        critical_failures.append(config["name"])
                else:
                    failure_count[port] = 0

            # Check if we need to restart
            if critical_failures and (current_time - last_restart) > 60:
                print(f"\n[WARN]  Critical failures detected: {', '.join(critical_failures)}")
                if restart_services():
                    last_restart = current_time
                    print("   ⏳ Waiting 30s for services to start...")
                    time.sleep(30)

            # Print status every 30 seconds
            if int(current_time) % 30 == 0:
                running = sum(1 for port in SERVICES if check_port(port))
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: {running}/{len(SERVICES)} services running")

            time.sleep(10)

        except KeyboardInterrupt:
            print("\n\n[EMOJI] Monitor stopped by user")
            break
        except Exception as e:
            print(f"\n[ERROR] Monitor error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    monitor_loop()
