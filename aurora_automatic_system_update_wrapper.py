#!/usr/bin/env python3
"""
Aurora Automatic System Update - Enhanced with Deep Search
Wrapper that runs the deep system updater for complete synchronization
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the deep system updater"""
    script_dir = Path(__file__).parent
    deep_updater = script_dir / "aurora_deep_system_updater.py"

    if deep_updater.exists():
        print("[STAR] Running Aurora Deep System Updater...")
        result = subprocess.run([sys.executable, str(deep_updater)])
        return result.returncode
    else:
        print("[ERROR] Deep updater not found!")
        return 1


if __name__ == "__main__":
    exit(main())
