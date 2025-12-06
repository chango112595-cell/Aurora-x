#!/usr/bin/env python3
"""
Aurora Global Enhancement Script
Integrates all Aurora systems including Memory Fabric 2.0
"""

import sys
import datetime
from pathlib import Path

def enhance_memory_system():
    """Integrate Aurora Memory Fabric 2.0"""
    print("[+] Integrating Aurora Memory Fabric...")
    try:
        from core.memory_manager import AuroraMemoryManager
        am = AuroraMemoryManager()
        am.remember_fact("integration_date", str(datetime.datetime.now()))
        am.remember_fact("fabric_version", "2.0-enhanced")
        am.save_message("system", "Aurora Memory Fabric 2.0 initialized.")
        print("[✓] Aurora Memory Fabric 2.0 integrated successfully")
        return True
    except Exception as e:
        print(f"[!] Memory system integration error: {e}")
        return False

def main():
    """Main enhancement routine"""
    print("=" * 60)
    print("AURORA GLOBAL ENHANCEMENT SYSTEM")
    print("=" * 60)
    
    # Check for --include-memory flag
    include_memory = "--include-memory" in sys.argv
    
    if include_memory:
        print("\n[*] Memory system enhancement requested")
        enhance_memory_system()
    else:
        print("\n[*] Run with --include-memory to integrate Memory Fabric 2.0")
    
    print("\n[✓] Enhancement complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
