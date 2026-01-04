#!/usr/bin/env python3
"""
aurora_runner.py
Unified process manager for Aurora-X Ultra.
Starts every service (Python + Node) in dependency order,
verifies health, and provides safe shutdown.
"""

import os
import subprocess
import sys
import signal
import time
import socket
from typing import List, Tuple, Optional

SERVICES = [
    {"name": "Memory Fabric V2", "cmd": ["python3", "aurora_memory_fabric_v2/service.py"], "port": 5004},
    {"name": "Memory Bridge",    "cmd": ["python3", "server/memory-bridge.py"],             "port": 5003},
    {"name": "Luminar Nexus V2", "cmd": ["python3", "tools/luminar_nexus_v2.py", "serve"], "port": 8000},
    {"name": "Aurora Nexus V3",  "cmd": ["python3", "aurora_nexus_v3/main.py"],            "port": 5002},
    {"name": "Express Server",   "cmd": ["npm", "run", "dev"],                             "port": 5000},
]

processes: List[Tuple[str, subprocess.Popen]] = []

def ensure_runtime():
    """Ensure modern Python >= 3.10 and Node >= 18."""
    try:
        pyv = sys.version_info
        if pyv < (3, 10):
            raise RuntimeError(f"Python 3.10+ required (found {pyv.major}.{pyv.minor})")
        print(f"Python {pyv.major}.{pyv.minor}.{pyv.micro}")
        
        nodev = subprocess.check_output(["node", "-v"], text=True).strip()
        major = int(nodev.split('.')[0].replace('v', ''))
        if major < 18:
            raise RuntimeError(f"Node 18+ required (found {nodev})")
        print(f"Node {nodev}")
        
        print("Runtime check passed")
    except FileNotFoundError as e:
        print(f"Runtime not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Runtime check failed: {e}")
        sys.exit(1)

def check_port(port: int, timeout: float = 1.0) -> bool:
    """Check if a port is accepting connections."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex(('127.0.0.1', port))
            return result == 0
    except:
        return False

def wait_for_port(port: int, timeout: int = 30) -> bool:
    """Wait for a port to become available."""
    start = time.time()
    while time.time() - start < timeout:
        if check_port(port):
            return True
        time.sleep(0.5)
    return False

def start_services():
    """Start all Aurora services in dependency order."""
    print("\n" + "=" * 60)
    print("  AURORA-X ULTRA - UNIFIED PROCESS MANAGER")
    print("  Starting all services in dependency order...")
    print("=" * 60 + "\n")
    
    for svc in SERVICES:
        name = svc["name"]
        cmd = svc["cmd"]
        port = svc["port"]
        
        print(f"Starting {name} on port {port}...")
        
        try:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            processes.append((name, p, port))
            
            if wait_for_port(port, timeout=15):
                print(f"  [OK] {name} is ready on port {port}")
            else:
                print(f"  [WARN] {name} started but port {port} not responding yet")
            
            time.sleep(1)
            
        except FileNotFoundError as e:
            print(f"  [SKIP] {name} - command not found: {cmd[0]}")
        except Exception as e:
            print(f"  [ERROR] {name} failed to start: {e}")
    
    print("\n" + "-" * 60)
    print("  All Aurora services launched.")
    print("-" * 60 + "\n")

def get_service_status():
    """Get current status of all services."""
    status = []
    for name, p, port in processes:
        alive = p.poll() is None
        port_open = check_port(port) if alive else False
        status.append({
            "name": name,
            "alive": alive,
            "port": port,
            "port_responding": port_open
        })
    return status

def print_status():
    """Print current service status."""
    status = get_service_status()
    print("\n--- Service Status ---")
    for s in status:
        icon = "" if s["alive"] and s["port_responding"] else "" if s["alive"] else ""
        print(f"  {icon} {s['name']} (port {s['port']})")
    print("-" * 25)

def monitor():
    """Monitor services and handle shutdown."""
    try:
        while True:
            live = [(name, p, port) for name, p, port in processes if p.poll() is None]
            
            if not live:
                print("  No live processes remaining - shutting down.")
                break
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n  Ctrl-C received; terminating processes...")
    finally:
        shutdown()

def shutdown():
    """Gracefully shutdown all services."""
    print("\nInitiating graceful shutdown...")
    
    for name, p, port in reversed(processes):
        if p.poll() is None:
            print(f"  Stopping {name}...")
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"  Force killing {name}...")
                p.kill()
    
    print("  Clean shutdown complete.")

def signal_handler(signum, frame):
    """Handle termination signals."""
    print(f"\n  Signal {signum} received...")
    shutdown()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    ensure_runtime()
    start_services()
    print_status()
    monitor()
