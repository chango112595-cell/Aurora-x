#!/usr/bin/env python3
"""
Aurora Universal Stop Command - Works on Windows, Linux, macOS
Stops all Aurora services with automatic platform detection.
"""

import contextlib
import os
import platform
import socket
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

IS_WINDOWS = platform.system() == "Windows"

# Aurora's ports
AURORA_PORTS = [
    5000,  # Backend API
    5001,  # Bridge
    5002,  # Nexus V3
    5003,  # Chat/Luminar Nexus (legacy)
    5004,  # Memory Fabric
    5005,  # Luminar Nexus V2 (legacy)
    5173,  # Vite frontend
    8000,  # Luminar Nexus V2
    8080,  # Alternative chat
]


def kill_port_windows(port: int) -> bool:
    """Kill process on Windows using netstat and taskkill"""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        for line in result.stdout.split("\n"):
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                if parts:
                    pid = parts[-1]
                    subprocess.run(
                        ["taskkill", "/F", "/PID", pid],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return True
        return False
    except Exception as e:
        print(f"   ⚠️  Error killing port {port}: {e}")
        return False


def kill_port_linux(port: int) -> bool:
    """Kill process running on a specific port using fuser/netstat"""
    try:
        # Use fuser if available (more reliable than lsof)
        result = subprocess.run(
            ["fuser", "-k", f"{port}/tcp"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except FileNotFoundError:
        # fuser not available, try netstat + kill
        try:
            result = subprocess.run(
                ["netstat", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            for line in result.stdout.split("\n"):
                if f":{port}" in line and "LISTEN" in line:
                    parts = line.split()
                    if len(parts) > 6 and "/" in parts[6]:
                        pid = parts[6].split("/")[0]
                        subprocess.run(["kill", "-9", pid], timeout=5)
                        return True
            return False
        except Exception:
            return False
    except Exception as e:
        print(f"   ⚠️  Error killing port {port}: {e}")
        return False


def kill_port(port: int) -> bool:
    """Kill process on port (cross-platform)"""
    if IS_WINDOWS:
        return kill_port_windows(port)
    else:
        return kill_port_linux(port)


def check_port(port_num: int) -> bool:
    """Check if a port is in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.5)
    try:
        result = sock.connect_ex(("127.0.0.1", port_num))
        sock.close()
        return result == 0
    except Exception:
        with contextlib.suppress(Exception):
            sock.close()
        return False


if __name__ == "__main__":
    print("🛑 Aurora: Stopping all services...")
    print("   Step 1: Killing processes on all ports...")

    stopped_count = 0
    for port in AURORA_PORTS:
        if check_port(port):
            if kill_port(port):
                print(f"   ✓ Stopped service on port {port}")
                stopped_count += 1
            else:
                print(f"   ⚠️  Could not stop service on port {port}")
        else:
            print(f"   ℹ️  No service running on port {port}")

    # Give processes time to die
    time.sleep(2)

    # Kill any Node.js or Python processes that might restart
    print("\n   Step 2: Ensuring all Aurora processes are stopped...")
    try:
        if IS_WINDOWS:
            # Windows: Kill processes by name
            for proc_name in ["node", "npm"]:
                subprocess.run(
                    ["taskkill", "/F", "/IM", f"{proc_name}.exe", "/T"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            print("   ✅ Killed all Aurora processes")
        else:
            # Linux/Unix: Use pkill
            processes = [
                "npm",
                "node",
                "tsx",
                "vite",
                "luminar_nexus",
                "self_learn",
                "aurora_x",
                "aurora_autonomous_monitor",
                "uvicorn",
            ]
            for proc in processes:
                subprocess.run(["pkill", "-9", "-f", proc], stderr=subprocess.DEVNULL)
            print("   ✅ Killed all Aurora processes")
    except Exception as e:
        print(f"   ⚠️  Process cleanup: {e}")

    # Stop tmux sessions if they exist (Linux/Unix only)
    if not IS_WINDOWS:
        print("\n   Step 3: Stopping tmux sessions...")
        try:
            sessions = [
                "aurora-backend",
                "aurora-vite",
                "aurora-bridge",
                "aurora-self-learn",
                "aurora-chat",
            ]
            for session in sessions:
                result = subprocess.run(
                    ["tmux", "has-session", "-t", session],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if result.returncode == 0:
                    subprocess.run(
                        ["tmux", "kill-session", "-t", session],
                        stderr=subprocess.DEVNULL,
                    )
                    print(f"   ✓ Killed tmux session: {session}")
        except Exception as e:
            print(f"   ℹ️  Tmux cleanup: {e}")
    else:
        print("\n   Step 3: Windows cleanup complete")

    # Clean up PID files
    print("\n   Step 4: Cleaning up PID files...")

    if IS_WINDOWS:
        pid_files = [
            "bridge.pid",
            "self_learn.pid",
            "luminar_keeper.pid",
            "aurora_orch.pid",
            ".self_learning.pid",
        ]
    else:
        pid_files = [
            "/tmp/bridge.pid",
            "/tmp/self_learn.pid",
            "/tmp/luminar_keeper.pid",
            "/tmp/aurora_orch.pid",
            ".self_learning.pid",
        ]

    for pid_file in pid_files:
        pid_path = ROOT / pid_file if not pid_file.startswith("/") else Path(pid_file)
        if pid_path.exists():
            try:
                pid_path.unlink()
                print(f"   ✓ Removed {pid_file}")
            except Exception as e:
                print(f"   ⚠️  Could not remove {pid_file}: {e}")

    print(f"\n✅ Stopped {stopped_count} services on ports")
    print("🌙 Aurora services are now offline")
    print("\n💡 All services stopped:")
    print("   • Backend API + Frontend")
    print("   • Bridge Service")
    print("   • Aurora Nexus V3")
    print("   • Luminar Nexus V2")
    print("   • Memory Fabric")
    print("   • Autonomous Monitor")
    print("\n   Aurora is completely shut down.")
