#!/usr/bin/env python3
"""
Aurora Diagnostic Viewer
- Reads and displays saved diagnostic data
- Shows service status without running anything
- Can be accessed via web interface
"""
import json
import socket
from datetime import datetime
from pathlib import Path


class DiagnosticViewer:
    def __init__(self):
        self.log_file = Path(__file__).parent / "services_status.log"
        self.diagnostics_file = Path(__file__).parent / "diagnostics.json"

    def read_latest_status(self):
        """Read the latest status from log file"""
        if not self.log_file.exists():
            return None

        with open(self.log_file) as f:
            lines = f.readlines()
            if lines:
                latest = json.loads(lines[-1])
                return latest
        return None

    def save_diagnostic_report(self):
        """Save current diagnostic snapshot"""
        ports = {
            5000: "Aurora UI (frontend)",
            5001: "Aurora backend (uvicorn)",
            5002: "Learning API / FastAPI",
            8080: "File Server",
            8000: "Standalone dashboards",
        }

        report = {"timestamp": datetime.now().isoformat(), "services": {}}

        for port, name in ports.items():
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            try:
                s.connect(("127.0.0.1", port))
                s.close()
                status = "UP"
            except:
                status = "DOWN"

            report["services"][port] = {"name": name, "status": status, "url": f"http://127.0.0.1:{port}"}

        with open(self.diagnostics_file, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def display_report(self):
        """Display diagnostic report in readable format"""
        report = self.save_diagnostic_report()

        print("\n" + "=" * 70)
        print("🔍 AURORA-X DIAGNOSTIC REPORT")
        print("=" * 70)
        print(f"\n⏰ Generated: {report['timestamp']}\n")

        print("SERVICE STATUS:")
        print("-" * 70)

        for port in sorted(report["services"].keys()):
            service = report["services"][port]
            status_icon = "✅" if service["status"] == "UP" else "❌"
            print(f"{status_icon} [PORT {port}] {service['name']}")
            print(f"   Status: {service['status']}")
            print(f"   URL: {service['url']}")
            print()

        print("=" * 70)

        # Check if all up
        all_up = all(s["status"] == "UP" for s in report["services"].values())
        if all_up:
            print("✨ ALL SERVICES OPERATIONAL\n")
        else:
            print("⚠️  SOME SERVICES OFFLINE\n")
            offline = [p for p, s in report["services"].items() if s["status"] == "DOWN"]
            print(f"Offline ports: {offline}\n")

        print("=" * 70 + "\n")

        return report

    def diagnose_port_5000(self):
        """Diagnose why port 5000 is offline"""
        print("\n" + "=" * 70)
        print("🔧 DIAGNOSING PORT 5000 (Aurora UI)")
        print("=" * 70 + "\n")

        # Check if process is running
        import subprocess

        print("1️⃣  Checking for Node.js processes...")
        try:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            node_processes = [line for line in result.stdout.split("\n") if "node" in line.lower()]
            if node_processes:
                print(f"   ✅ Found {len(node_processes)} Node.js process(es):")
                for proc in node_processes[:3]:
                    print(f"      {proc.strip()[:80]}")
            else:
                print("   ❌ No Node.js processes found")
        except:
            print("   ⚠️  Could not check processes")

        print("\n2️⃣  Checking port 5000 specifically...")
        try:
            result = subprocess.run(["netstat", "-tlnp"], capture_output=True, text=True)
            port_5000 = [line for line in result.stdout.split("\n") if ":5000" in line]
            if port_5000:
                print("   ✅ Port 5000 is LISTENING:")
                for line in port_5000:
                    print(f"      {line.strip()}")
            else:
                print("   ❌ Port 5000 is NOT LISTENING")
        except:
            print("   ⚠️  Could not check with netstat, trying lsof...")
            try:
                result = subprocess.run(["lsof", "-i", ":5000"], capture_output=True, text=True)
                if result.stdout:
                    print(f"   ✅ Process on port 5000: {result.stdout}")
                else:
                    print("   ❌ Port 5000 is FREE (not in use)")
            except:
                print("   ⚠️  Could not check with lsof either")

        print("\n3️⃣  Checking Express server file...")
        server_file = Path("/workspaces/Aurora-x/server.js")
        if server_file.exists():
            print("   ✅ server.js exists")
        else:
            print(f"   ❌ server.js NOT FOUND at {server_file}")

        print("\n4️⃣  Recommended Actions:")
        print("   • Start Express: cd /workspaces/Aurora-x && node server.js")
        print("   • Check logs: tail -f /workspaces/Aurora-x/*.log")
        print("   • Rebuild frontend: cd /workspaces/Aurora-x/client && npm run build")

        print("\n" + "=" * 70 + "\n")


def main():
    viewer = DiagnosticViewer()

    # Display report
    report = viewer.display_report()

    # Diagnose port 5000
    viewer.diagnose_port_5000()

    # Save for web access
    print("📁 Report saved to: tools/diagnostics.json")
    print("   Can be viewed via web interface\n")


if __name__ == "__main__":
    main()
