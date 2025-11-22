#!/usr/bin/env python3
"""
Aurora Core Activation Script
Loads aurora_core.py and activates all integrated autonomous modules
Runs as a background daemon to coordinate all systems
"""

import sys
import time
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tools"))


def activate_aurora_core():
    """Activate Aurora Core and all integrated modules"""
    print("🧠 Aurora Core: Initializing...")

    try:
        from aurora_core import create_aurora_core

        # Create Aurora instance
        aurora = create_aurora_core()
        print(f"   ✅ Aurora Core loaded: {aurora.__class__.__name__}")

        # Check for integrated modules
        if hasattr(aurora, 'integrated_modules'):
            modules = aurora.integrated_modules
            print(f"   📦 Integrated modules: {len(modules)}")

            for name, module in modules.items():
                print(
                    f"      • {name}: {'✅ Active' if module else '⚠️ Not loaded'}")

                # If module has activation methods, call them
                if module:
                    # Try to start monitoring if available
                    if hasattr(module, 'start_monitoring'):
                        try:
                            print(
                                f"        🔄 Starting monitoring for {name}...")
                            threading.Thread(
                                target=module.start_monitoring, daemon=True).start()
                        except Exception as e:
                            print(
                                f"        ⚠️ Could not start monitoring: {e}")

                    # Try to activate if available
                    if hasattr(module, 'activate'):
                        try:
                            print(f"        ⚡ Activating {name}...")
                            module.activate()
                        except Exception as e:
                            print(f"        ⚠️ Could not activate: {e}")

                    # Try to start daemon mode if available
                    if hasattr(module, 'start_daemon'):
                        try:
                            print(f"        👁️ Starting daemon for {name}...")
                            threading.Thread(
                                target=module.start_daemon, daemon=True).start()
                        except Exception as e:
                            print(f"        ⚠️ Could not start daemon: {e}")

        print("\n   ✅ Aurora Core fully activated")
        print("   🔮 All integrated modules are now coordinating")

        # Keep the process alive for background coordination
        print("   👁️ Background coordination active...")

        # Run a simple heartbeat loop
        while True:
            time.sleep(60)  # Check every minute
            # This keeps the process alive and allows daemon threads to run

    except ImportError as e:
        print(f"   ❌ Could not import aurora_core: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Activation error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        activate_aurora_core()
    except KeyboardInterrupt:
        print("\n   👋 Aurora Core activation stopped")
        sys.exit(0)
