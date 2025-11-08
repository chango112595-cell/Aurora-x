#!/usr/bin/env python3
"""
Aurora Restarts Herself
========================
Aurora stops all old services and reloads herself with the new UI
"""

import os
import subprocess
import time
from pathlib import Path


class AuroraSelfReload:
    """Aurora reloads herself autonomously."""

    def __init__(self):
        self.root = Path(__file__).parent.parent

    def log(self, emoji: str, message: str):
        print(f"{emoji} {message}")

    def stop_all_services(self):
        """Aurora stops all her old services."""
        self.log("🛑", "Aurora stopping all old services...")
        print()

        # Kill all node processes on port 5000
        self.log("1️⃣", "Stopping UI servers on port 5000...")
        subprocess.run(["pkill", "-f", "vite"], capture_output=True)
        subprocess.run(["pkill", "-f", "npm run dev"], capture_output=True)
        subprocess.run(["fuser", "-k", "5000/tcp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

        # Verify port is free
        result = subprocess.run(["lsof", "-i", ":5000", "-P", "-n"], capture_output=True, text=True)
        if result.stdout:
            self.log("⚠️", "Port 5000 still in use, force killing...")
            subprocess.run(["fuser", "-k", "-9", "5000/tcp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
        else:
            self.log("✅", "Port 5000 is free")

        print()

    def clear_caches(self):
        """Aurora clears all caches."""
        self.log("🧹", "Aurora clearing caches...")
        print()

        # Clear build artifacts
        subprocess.run(["rm", "-rf", str(self.root / "client" / ".vite")], capture_output=True)
        subprocess.run(["rm", "-rf", str(self.root / "client" / "dist")], capture_output=True)
        subprocess.run(["rm", "-rf", str(self.root / "dist")], capture_output=True)
        subprocess.run(["rm", "-rf", str(self.root / ".vite")], capture_output=True)

        self.log("✅", "Caches cleared")
        print()

    def start_new_ui(self):
        """Aurora starts her new UI."""
        self.log("🚀", "Aurora starting her new UI...")
        print()

        # Start in background
        os.chdir(str(self.root / "client"))

        # Start dev server in background
        subprocess.Popen(
            ["npm", "run", "dev"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(self.root / "client")
        )

        self.log("⏳", "Waiting for UI to start...")
        time.sleep(8)

        # Verify it's running
        result = subprocess.run(["lsof", "-i", ":5000", "-P", "-n"], capture_output=True, text=True)
        if ":5000" in result.stdout:
            self.log("✅", "Aurora UI is running on port 5000!")
        else:
            self.log("⚠️", "UI might still be starting...")

        print()

    def run(self):
        """Aurora's complete self-reload process."""
        print("🌟" * 35)
        print("AURORA RELOADING HERSELF")
        print("🌟" * 35)
        print()

        self.stop_all_services()
        self.clear_caches()
        self.start_new_ui()

        print("=" * 70)
        self.log("✅", "AURORA RELOADED!")
        print("=" * 70)
        print()
        print("🌟 Aurora says:")
        print("   'I've stopped all old services and started fresh with my new UI!'")
        print()
        print("Next steps:")
        print("   1. Open http://localhost:5000/chat in your browser")
        print("   2. Clear browser cache (Ctrl+Shift+R)")
        print("   3. Unregister service workers (F12 → Application → Service Workers)")
        print("   4. You should see my new Aurora chat interface! 🌟")
        print()


if __name__ == "__main__":
    aurora = AuroraSelfReload()
    aurora.run()
