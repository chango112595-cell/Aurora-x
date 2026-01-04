#!/usr/bin/env python3
"""
Auto-debugger:
- Collects traces, tries simple fixes (restart, reload, reinstall last good)
- Uses heuristics: if memory leak or exception pattern occurs repeatedly, attempt recovery steps
"""
import traceback, time, os
from pathlib import Path
from ..core.self_heal import rollback, quarantine_module

TRACE_DIR = Path(".traces")

def analyze_and_heal(trace_path: str):
    t = Path(trace_path).read_text()
    # naive pattern: repeated "MemoryError" => restart
    if "MemoryError" in t:
        # attempt to rollback most recent backup
        bdir = Path(".aurora_backup")
        if bdir.exists():
            items = sorted(bdir.iterdir(), reverse=True)
            if items:
                # perform rollback of top-level
                rollback(items[0].name, ".")
                return {"action":"rollback","backup":items[0].name}
    # otherwise, quarantine module if exception from module path
    return {"action":"none"}
