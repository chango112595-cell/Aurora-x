"""
sandbox.py - helper utilities for sandbox execution.

Key responsibilities:
- create per-pack working directories (VFS)
- apply simple chroot-like isolation by running commands with cwd inside pack vfs
- set basic resource limits using Python `resource` where available
- fall back gracefully on platforms without `resource` (Windows)
"""
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional
try:
    import resource as _resource
except Exception:
    _resource = None

from .vfs import VirtualFS

ROOT = Path(__file__).resolve().parents[2]

def ensure_sandbox_dirs(pack_id: str):
    v = VirtualFS(pack_id)
    # create default structure
    for d in ("tmp","run","logs"):
        (v.path(d)).mkdir(parents=True, exist_ok=True)
    return v

def set_limits(memory_mb: Optional[int] = None, cpu_seconds: Optional[int] = None):
    """
    set soft limits in-process (applies to current process). For subprocesses,
    the caller should spawn a shim that sets limits before exec.
    """
    if _resource is None:
        return False
    try:
        if memory_mb:
            # RLIMIT_AS (address space) limit in bytes
            _resource.setrlimit(_resource.RLIMIT_AS, (memory_mb * 1024 * 1024, _resource.RLIM_INFINITY))
        if cpu_seconds:
            _resource.setrlimit(_resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        return True
    except Exception:
        return False

def run_in_sandbox(pack_id: str, cmd: str, timeout: int = 30, capture=True):
    v = ensure_sandbox_dirs(pack_id)
    workdir = str(v.path("."))
    # Launch process with cwd set to workdir
    # We purposely do not attempt to change root; instead we run in the pack's vfs root
    args = cmd if isinstance(cmd, (list, tuple)) else ["/bin/sh", "-c", cmd]
    p = subprocess.Popen(args, cwd=workdir, stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE if capture else None)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        return {"rc": -1, "timeout": True, "stdout": (out.decode() if out else ""), "stderr": (err.decode() if err else "")}
    return {"rc": p.returncode, "stdout": (out.decode() if out else ""), "stderr": (err.decode() if err else "")}

def run_background(pack_id: str, cmd: str):
    v = ensure_sandbox_dirs(pack_id)
    workdir = str(v.path("."))
    p = subprocess.Popen(cmd, cwd=workdir, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return p.pid
