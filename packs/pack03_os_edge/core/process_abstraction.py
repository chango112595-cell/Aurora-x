"""
Process abstraction for packs: provides safe subprocess execution wrapper,
timeout, and output capture. Keeps all process artifacts inside pack data.
"""
import subprocess, shlex, os, time
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]

class PackProcess:
    def __init__(self, pack_id: str, workdir: Optional[str]=None):
        self.pack_id = pack_id
        self.workdir = Path(workdir) if workdir else (ROOT / "data" / "vfs" / pack_id)
        self.workdir.mkdir(parents=True, exist_ok=True)

    def run(self, cmd: str, timeout: Optional[int]=30, capture=True):
        args = shlex.split(cmd)
        p = subprocess.Popen(args, cwd=str(self.workdir), stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE if capture else None)
        try:
            out, err = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            out, err = p.communicate()
            return {"rc": -1, "timeout": True, "stdout": out.decode() if out else "", "stderr": err.decode() if err else ""}
        return {"rc": p.returncode, "stdout": out.decode() if out else "", "stderr": err.decode() if err else ""}

    def run_background(self, cmd: str):
        args = shlex.split(cmd)
        p = subprocess.Popen(args, cwd=str(self.workdir), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return p.pid
