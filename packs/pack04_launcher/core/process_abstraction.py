#!/usr/bin/env python3
"""
process_abstraction.py - Local wrapper for pack04 that provides PackProcess.
Imports from pack03 when available, otherwise provides compatible fallback.
"""
import subprocess, shlex, os
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]

try:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pack03_os_base"))
    from core.process_abstraction import PackProcess as Pack03Process
    _HAS_PACK03 = True
except ImportError:
    _HAS_PACK03 = False

class PackProcess:
    def __init__(self, pack_id: str, workdir: Optional[str]=None):
        self.pack_id = pack_id
        self.workdir = Path(workdir) if workdir else (ROOT / "data" / "vfs" / pack_id)
        self.workdir.mkdir(parents=True, exist_ok=True)

    def run(self, cmd: str, timeout: Optional[int]=30, capture=True):
        args = shlex.split(cmd)
        try:
            p = subprocess.Popen(
                args, 
                cwd=str(self.workdir), 
                stdout=subprocess.PIPE if capture else None, 
                stderr=subprocess.PIPE if capture else None
            )
            out, err = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            out, err = p.communicate()
            return {"rc": -1, "timeout": True, "stdout": out.decode() if out else "", "stderr": err.decode() if err else ""}
        except FileNotFoundError:
            return {"rc": -1, "stderr": f"command not found: {args[0] if args else cmd}"}
        return {"rc": p.returncode, "stdout": out.decode() if out else "", "stderr": err.decode() if err else ""}

    def run_background(self, cmd: str):
        args = shlex.split(cmd)
        p = subprocess.Popen(args, cwd=str(self.workdir), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return p.pid
