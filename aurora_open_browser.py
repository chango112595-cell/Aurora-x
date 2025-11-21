#!/usr/bin/env python3
"""
Aurora Autonomous Browser Launcher
Opens Aurora's dashboard automatically in the default browser
"""

import socket
import time
import webbrowser


class AuroraBrowserLauncher:
    """Aurora opens her own interface in the browser"""

    def __init__(self):
        self.frontend_url = "http://localhost:5000"
        self.dashboard_url = "http://localhost:5005"

    def log(self, message):
        print(f"[Aurora] {message}")

    def check_port(self, port):
        """Check if a port is accessible"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", port))
        sock.close()
        return result == 0

    def wait_for_service(self, port, max_wait=10):
        """Wait for a service to be ready"""
        self.log(f"Waiting for service on port {port}...")
        for _i in range(max_wait):
            if self.check_port(port):
                self.log(f"✅ Port {port} is ready!")
                return True
            time.sleep(1)
        return False

    def open_dashboard(self):
        """Open Aurora's dashboard in browser"""
        self.log("🌌 Opening Aurora Dashboard...")

        # Wait for backend to be ready
        if not self.wait_for_service(5000):
            self.log("⚠️  Backend not ready, but attempting to open browser anyway...")

        # Open the dashboard
        try:
            webbrowser.open(self.frontend_url)
            self.log(f"🚀 Opened: {self.frontend_url}")
            self.log("✅ Aurora's futuristic dashboard should now be visible!")
            return True
        except Exception as e:
            self.log(f"❌ Could not open browser: {e}")
            self.log(f"💡 Please manually open: {self.frontend_url}")
            return False

    def execute(self):
        """Execute browser launch"""
        self.log("=" * 70)
        self.log("🌌 AURORA AUTONOMOUS BROWSER LAUNCHER")
        self.log("=" * 70)
        self.log("")

        success = self.open_dashboard()

        self.log("")
        self.log("=" * 70)
        if SUCCESS:
            self.log("✅ BROWSER LAUNCHED")
            self.log(f"📍 URL: {self.frontend_url}")
            self.log("🎨 You should see Aurora's futuristic quantum neural dashboard")
            self.log("")
            self.log("Features visible:")
            self.log("  • Quantum Coherence Monitor")
            self.log("  • 13 Foundational Tasks Matrix")
            self.log("  • 34 Knowledge Tiers Architecture")
            self.log("  • 5 Service Status Grid")
            self.log("  • Neural Activity Monitor")
        else:
            self.log(f"💡 Manual access: {self.frontend_url}")
        self.log("=" * 70)

        return success


if __name__ == "__main__":
    print("\n🌌 Aurora: Autonomous Browser Launcher\n")
    launcher = AuroraBrowserLauncher()
    launcher.execute()
    print("\n✨ Aurora has launched her interface!")
