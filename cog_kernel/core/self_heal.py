#!/usr/bin/env python3
"""
Self-healing engine:
- Can rollback to last known-good (via backups)
- Restart hung modules or processes
- Mark components as quarantined
"""

import shutil
from pathlib import Path

BACKUP_DIR = Path(".aurora_backup")
QUARANTINE = Path(".aurora_quarantine")
QUARANTINE.mkdir(exist_ok=True)


def rollback(backup_ts: str, target: str):
    b = BACKUP_DIR / backup_ts
    if not b.exists():
        raise FileNotFoundError("backup missing")
    # naive restore
    shutil.copytree(b, Path(target), dirs_exist_ok=True)
    return True


def quarantine_module(path: str):
    p = Path(path)
    if not p.exists():
        return False
    dest = QUARANTINE / p.name
    p.rename(dest)
    return True
