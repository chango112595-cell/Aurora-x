#!/usr/bin/env python3
"""
Aurora Memory System - Backup and Security Utilities
"""

import os
import shutil
import hashlib
import datetime
from pathlib import Path


def backup_memory(base_path: str = "data/memory"):
    """Create a backup of the memory system"""
    src = base_path
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    dst = f"backups/memory_{timestamp}.zip"

    # Create backups directory
    Path("backups").mkdir(exist_ok=True)

    # Create zip archive
    shutil.make_archive(dst.replace(".zip", ""), "zip", src)
    print(f"[✓] Memory backup created → {dst}")
    return dst


def verify_integrity(base_path: str = "data/memory"):
    """Verify integrity of memory files"""
    print("[*] Verifying memory integrity...")

    for root, _, files in os.walk(base_path):
        for f in files:
            path = os.path.join(root, f)
            try:
                with open(path, "rb") as file:
                    content = file.read()
                    h = hashlib.sha256(content).hexdigest()
                    print(f"✓ {path}: {h}")
            except Exception as e:
                print(f"✗ {path}: Error - {e}")

    print("[✓] Integrity check complete")


if __name__ == "__main__":
    backup_memory()
    verify_integrity()
