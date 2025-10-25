
#!/usr/bin/env python3
"""Aurora-X Server Manager - Monitor and fix server issues"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path


def check_port(port: int) -> dict:
    """Check if a port is in use and what's using it"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        for line in result.stdout.splitlines():
            if f":{port}" in line or f"port {port}" in line or f"{port}" in line:
                return {
                    "port": port,
                    "in_use": True,
                    "process": line.strip()
                }
        
        return {"port": port, "in_use": False, "process": None}
    except Exception as e:
        return {"port": port, "in_use": False, "error": str(e)}


def check_server_health(url: str) -> dict:
    """Check if server responds to health check"""
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=3) as response:
            data = response.read().decode()
            return {
                "url": url,
                "status": response.status,
                "healthy": True,
                "response": data[:200]
            }
    except Exception as e:
        return {
            "url": url,
            "healthy": False,
            "error": str(e)
        }


def get_running_workflows() -> list:
    """Get list of running workflows"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        workflows = []
        for line in result.stdout.splitlines():
            if "aurora_x" in line.lower() or "uvicorn" in line or "node" in line:
                workflows.append(line.strip())
        
        return workflows
    except Exception as e:
        return [f"Error: {e}"]


def kill_process_on_port(port: int) -> bool:
    """Kill process using specified port"""
    try:
        # Find PID using the port
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        for line in result.stdout.splitlines():
            if f":{port}" in line or f"port {port}" in line:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    subprocess.run(["kill", "-9", pid], timeout=5)
                    print(f"✓ Killed process {pid} on port {port}")
                    return True
        
        return False
    except Exception as e:
        print(f"✗ Error killing process on port {port}: {e}")
        return False


def start_web_server() -> bool:
    """Start the main web server (Node/Express)"""
    try:
        print("🚀 Starting web server on port 5000...")
        subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)
        return True
    except Exception as e:
        print(f"✗ Failed to start web server: {e}")
        return False


def start_bridge_service() -> bool:
    """Start the Python Bridge service"""
    try:
        print("🌉 Starting Bridge service on port 5001...")
        subprocess.Popen(
            ["bash", "scripts/bridge_autostart.sh"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)
        return True
    except Exception as e:
        print(f"✗ Failed to start Bridge: {e}")
        return False


def print_status():
    """Print comprehensive server status"""
    print("\n" + "="*60)
    print("🔍 AURORA-X SERVER MANAGER")
    print("="*60)
    
    # Check ports
    print("\n📡 PORT STATUS:")
    ports = [5000, 5001]
    for port in ports:
        status = check_port(port)
        if status["in_use"]:
            print(f"  Port {port}: 🟢 IN USE")
            if status.get("process"):
                print(f"    {status['process'][:80]}")
        else:
            print(f"  Port {port}: 🔴 AVAILABLE")
    
    # Check health endpoints
    print("\n🏥 HEALTH CHECKS:")
    endpoints = [
        ("http://0.0.0.0:5000/api/health", "Main Web Server"),
        ("http://0.0.0.0:5001/healthz", "Python Bridge"),
    ]
    
    for url, name in endpoints:
        health = check_server_health(url)
        if health["healthy"]:
            print(f"  {name}: 🟢 HEALTHY ({health['status']})")
        else:
            print(f"  {name}: 🔴 DOWN - {health.get('error', 'Unknown')}")
    
    # Check running processes
    print("\n⚙️  RUNNING PROCESSES:")
    workflows = get_running_workflows()
    if workflows:
        for wf in workflows[:5]:  # Limit to first 5
            print(f"  • {wf[:80]}")
    else:
        print("  No Aurora processes found")
    
    print("\n" + "="*60)


def auto_fix():
    """Automatically fix common server issues"""
    print("\n🔧 AUTO-FIX MODE")
    print("="*60)
    
    # Check if web server is running
    web_health = check_server_health("http://0.0.0.0:5000/api/health")
    
    if not web_health["healthy"]:
        print("\n⚠️  Web server not responding on port 5000")
        print("   Attempting to restart...")
        
        # Kill any process on port 5000
        kill_process_on_port(5000)
        time.sleep(1)
        
        # Start web server
        if start_web_server():
            time.sleep(3)
            # Verify it started
            web_health = check_server_health("http://0.0.0.0:5000/api/health")
            if web_health["healthy"]:
                print("✅ Web server started successfully!")
            else:
                print("❌ Web server failed to start")
    else:
        print("✅ Web server is healthy")
    
    # Check if bridge is running
    bridge_health = check_server_health("http://0.0.0.0:5001/healthz")
    
    if not bridge_health["healthy"]:
        print("\n⚠️  Bridge service not responding on port 5001")
        print("   Attempting to restart...")
        
        kill_process_on_port(5001)
        time.sleep(1)
        
        if start_bridge_service():
            time.sleep(2)
            bridge_health = check_server_health("http://0.0.0.0:5001/healthz")
            if bridge_health["healthy"]:
                print("✅ Bridge service started successfully!")
            else:
                print("❌ Bridge service failed to start")
    else:
        print("✅ Bridge service is healthy")
    
    print("\n" + "="*60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora-X Server Manager")
    parser.add_argument("--status", action="store_true", help="Show server status")
    parser.add_argument("--fix", action="store_true", help="Auto-fix server issues")
    parser.add_argument("--kill-port", type=int, help="Kill process on specified port")
    parser.add_argument("--start-web", action="store_true", help="Start web server")
    parser.add_argument("--start-bridge", action="store_true", help="Start bridge service")
    
    args = parser.parse_args()
    
    if args.kill_port:
        kill_process_on_port(args.kill_port)
    elif args.start_web:
        start_web_server()
        time.sleep(3)
        print_status()
    elif args.start_bridge:
        start_bridge_service()
        time.sleep(2)
        print_status()
    elif args.fix:
        auto_fix()
        print("\n📊 FINAL STATUS:")
        print_status()
    else:
        # Default: show status
        print_status()
        print("\n💡 USAGE:")
        print("  python tools/server_manager.py --status    # Show status")
        print("  python tools/server_manager.py --fix       # Auto-fix issues")
        print("  python tools/server_manager.py --kill-port 5000  # Kill port")
        print("  python tools/server_manager.py --start-web # Start web server")


if __name__ == "__main__":
    main()
