#!/usr/bin/env python3
"""
Aurora Memory Fabric - Backup Job
----------------------------------
Scheduled backup of all memory data with integrity verification.

Run as cron job:
  0 2 * * * python3 /path/to/backup_memory.py

Author: Aurora AI System
Version: 2.0-enhanced
"""

import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.memory_fabric import AuroraMemoryFabric


def run_backup():
    """Execute memory backup with integrity check"""
    print(f"[Backup] Starting at {datetime.datetime.now()}")
    
    am = AuroraMemoryFabric()
    
    integrity = am.integrity_hash()
    print(f"[Backup] Verified {len(integrity)} memory files")
    
    backup_path = am.backup(backup_dir="backups/memory")
    
    print(f"[Backup] Completed: {backup_path}")
    print(f"[Backup] Finished at {datetime.datetime.now()}")
    
    return backup_path


if __name__ == "__main__":
    run_backup()