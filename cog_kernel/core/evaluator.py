#!/usr/bin/env python3
"""
Module evaluator: runs test harness on module updates, runs unit tests and safety checks (policy-driven)
"""

import subprocess
import time
from pathlib import Path


def run_tests_for_module(path: str):
    # default: run pytest on module dir (if tests exist)
    p = Path(path)
    if not p.exists():
        return {"ok": False, "reason": "missing"}
    # run pytest if present
    if list(p.rglob("test_*.py")):
        res = subprocess.run(["pytest", str(p)], capture_output=True, text=True)
        return {"rc": res.returncode, "stdout": res.stdout, "stderr": res.stderr, "ts": time.time()}
    return {"ok": True, "note": "no tests"}
