#!/usr/bin/env python3
"""
Aurora's Autonomous Dashboard Loader
Created by Aurora - Complete implementation with NO TODOs
"""
import subprocess
import time
import webbrowser
from pathlib import Path


class AuroraDashboardLoader:
    def __init__(self):
        self.vite_url = "http://localhost:5000"
        self.dashboard_routes = ["/aurora-dashboard", "/dashboard", "/"]

    def check_server_status(self):
        """Check if Vite server is running"""
        try:
            result = subprocess.run(["curl", "-s", "-I", self.vite_url], capture_output=True, text=True, timeout=5)

            if "200 OK" in result.stdout:
                print("[OK] Server is running")
                return True
            else:
                print("[ERROR] Server not responding")
                return False
        except Exception as e:
            print(f"[ERROR] Server check failed: {e}")
            return False

    def start_server(self):
        """Start Vite development server if not running"""
        print("[LAUNCH] Starting Vite server...")

        # Kill any existing processes
        subprocess.run(["pkill", "-f", "vite"], capture_output=True)
        subprocess.run(["pkill", "-f", "5000"], capture_output=True)
        time.sleep(2)

        # Change to client directory and start server
        import os

        os.chdir("/workspaces/Aurora-x/client")

        # Start Vite in background
        process = subprocess.Popen(["npm", "run", "dev"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(f"⏳ Server starting (PID: {process.pid})...")
        time.sleep(5)

        # Verify it started
        if self.check_server_status():
            print("[OK] Server started successfully")
            return True
        else:
            print("[WARN]  Server may still be starting...")
            return False

    def find_dashboard_route(self):
        """Find which dashboard route exists"""
        app_file = Path("/workspaces/Aurora-x/client/src/App.tsx")

        if app_file.exists():
            content = app_file.read_text()

            for route in self.dashboard_routes:
                if route in content.lower():
                    print(f"[OK] Found dashboard route: {route}")
                    return route

        # Default to home page
        print("ℹ️  Using default route: /")
        return "/"

    def open_dashboard(self, route="/"):
        """Open dashboard in browser"""
        url = f"{self.vite_url}{route}"
        print(f"[WEB] Opening dashboard at: {url}")

        try:
            webbrowser.open(url)
            print("[OK] Dashboard opened")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to open browser: {e}")
            return False

    def load_dashboard(self):
        """Main method to load Aurora's dashboard"""
        print("\n" + "=" * 60)
        print("[STAR] AURORA DASHBOARD LOADER")
        print("=" * 60 + "\n")

        # Step 1: Check if server is running
        if not self.check_server_status():
            # Step 2: Start server if needed
            if not self.start_server():
                print("[ERROR] Failed to start server")
                return False

        # Step 3: Find dashboard route
        route = self.find_dashboard_route()

        # Step 4: Open dashboard
        if self.open_dashboard(route):
            print("\n[OK] Aurora Dashboard loaded successfully!")
            return True
        else:
            print("\n[ERROR] Failed to load dashboard")
            return False


if __name__ == "__main__":
    loader = AuroraDashboardLoader()
    loader.load_dashboard()
