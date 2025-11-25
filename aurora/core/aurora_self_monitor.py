"""
Aurora's Self-Monitoring & Auto-Fix System
==========================================
Created by Aurora to monitor herself and auto-fix issues.

Aurora's personality:
- Proactive: Detects problems before users notice
- Smart: Learns from patterns
- Fast: Fixes instantly
- Transparent: Logs everything she does
"""

import asyncio
import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


class AuroraSelfMonitor:
    """
    Aurora monitors her own health and fixes issues automatically.

    This is Aurora's own design - she knows what she needs to watch.
    """

    def __init__(self):
        """
              Init  
            
            Args:
            """
        self.root = Path(__file__).parent.parent
        self.health_log = self.root / ".aurora_knowledge" / "health_log.jsonl"
        self.auto_fixes_log = self.root / ".aurora_knowledge" / "auto_fixes.jsonl"
        self.health_log.parent.mkdir(exist_ok=True)

        # Aurora's monitoring configuration
        self.services = {
            "ui": {"port": 5000, "name": "Aurora UI", "critical": True},
            "backend": {"port": 5001, "name": "Backend API", "critical": True},
            "learning": {"port": 5002, "name": "Learning Engine", "critical": False},
            "chat": {"port": 8080, "name": "Chat Server", "critical": False},
        }

        self.check_interval = 10  # Aurora checks every 10 seconds
        self.auto_fix_enabled = True  # Aurora fixes automatically

    async def check_service_health(self, service_key: str) -> dict[str, Any]:
        """Aurora checks if a service is healthy."""
        service = self.services[service_key]
        port = service["port"]

        health = {
            "service": service_key,
            "name": service["name"],
            "port": port,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
        }

        # Check 1: Port listening
        try:
            result = subprocess.run(["lsof", "-i", f":{port}", "-P", "-n"], capture_output=True, text=True, timeout=2)
            port_listening = result.returncode == 0 and result.stdout
            health["checks"]["port_listening"] = port_listening
        except Exception as e:
            health["checks"]["port_listening"] = False
            health["checks"]["port_error"] = str(e)

        # Check 2: HTTP health endpoint (if applicable)
        if service_key in ["backend", "chat"]:
            try:
                req = urllib.request.Request(f"http://localhost:{port}/health")
                with urllib.request.urlopen(req, timeout=2) as response:
                    health["checks"]["http_responding"] = response.status == 200
            except Exception as e:
                health["checks"]["http_responding"] = False
                health["checks"]["http_error"] = str(e)

        # Overall status
        if health["checks"].get("port_listening"):
            health["status"] = "healthy"
        else:
            health["status"] = "down" if service["critical"] else "degraded"

        return health

    async def auto_fix_service(self, service_key: str):
        """Aurora automatically fixes a broken service."""
        service = self.services[service_key]

        print(f"[EMOJI] Aurora auto-fixing {service['name']}...")

        fix_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": service_key,
            "action": "auto_restart",
            "reason": "Service down detected",
        }

        try:
            # Aurora restarts the service
            result = subprocess.run(
                ["/bin/python3", "tools/aurora_supervisor.py", "restart", "--service", service_key],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            fix_log["success"] = result.returncode == 0
            fix_log["output"] = result.stdout

            if result.returncode == 0:
                print(f"   [OK] Aurora fixed {service['name']}")
            else:
                print(f"   [WARN]  Auto-fix failed: {result.stderr}")
                fix_log["error"] = result.stderr

        except Exception as e:
            fix_log["success"] = False
            fix_log["error"] = str(e)
            print(f"   [ERROR] Auto-fix error: {e}")

        # Log the fix attempt
        with open(self.auto_fixes_log, "a") as f:
            f.write(json.dumps(fix_log) + "\n")

        return fix_log["success"]

    async def monitor_loop(self):
        """Aurora's main monitoring loop."""
        print("[STAR] Aurora Self-Monitor ACTIVE")
        print(f"   Checking services every {self.check_interval} seconds")
        print(f"   Auto-fix: {'ENABLED' if self.auto_fix_enabled else 'DISABLED'}")
        print()

        iteration = 0

        while True:
            iteration += 1
            print(f"\n[SCAN] Health check #{iteration} - {datetime.now().strftime('%H:%M:%S')}")

            # Check all services
            health_results = {}
            for service_key in self.services:
                health = await self.check_service_health(service_key)
                health_results[service_key] = health

                # Display status
                status_icon = "[OK]" if health["status"] == "healthy" else "[ERROR]"
                print(f"   {status_icon} {health['name']}: {health['status']}")

                # Auto-fix if needed
                if health["status"] != "healthy" and self.auto_fix_enabled:
                    if self.services[service_key]["critical"]:
                        print("      [EMOJI] Critical service down! Auto-fixing...")
                        await self.auto_fix_service(service_key)

            # Log health check
            with open(self.health_log, "a") as f:
                f.write(
                    json.dumps(
                        {"timestamp": datetime.utcnow().isoformat(), "iteration": iteration, "results": health_results}
                    )
                    + "\n"
                )

            # Aurora's smart analysis
            all_healthy = all(h["status"] == "healthy" for h in health_results.values())
            if all_healthy:
                print("   [STAR] All systems nominal")

            await asyncio.sleep(self.check_interval)

    def get_health_summary(self) -> dict[str, Any]:
        """Get Aurora's health monitoring summary."""
        if not self.health_log.exists():
            return {"status": "no_data", "message": "Monitoring not started yet"}

        # Read last 10 health checks
        with open(self.health_log) as f:
            lines = f.readlines()
            recent = [json.loads(line) for line in lines[-10:]]

        if not recent:
            return {"status": "no_data"}

        latest = recent[-1]

        return {
            "status": "monitoring_active",
            "last_check": latest["timestamp"],
            "iteration": latest["iteration"],
            "services": latest["results"],
            "total_checks": len(lines),
        }


async def main():
    """Start Aurora's self-monitoring."""
    monitor = AuroraSelfMonitor()
    await monitor.monitor_loop()


if __name__ == "__main__":
    asyncio.run(main())
