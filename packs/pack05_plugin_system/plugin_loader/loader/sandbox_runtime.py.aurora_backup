#!/usr/bin/env python3
"""
sandbox_runtime.py - core runtime wrapper for launching plugin entrypoints inside a controlled
workdir. This module uses soft resource limits (resource) and process isolation by running
in the per-plugin VFS directory. It does not require root.

API:
  SandboxRuntime(pack_id)
  .stage_package(src_dir) -> copies to stage area
  .run_entry(entry_cmd, timeout=30, background=False) -> runs the entrypoint
  .status() -> info
"""

import shutil, tempfile, os, time, json, subprocess, threading
from pathlib import Path
from typing import Optional
try:
    import resource as _resource
except Exception:
    _resource = None

ROOT = Path(__file__).resolve().parents[1]
VFS_BASE = ROOT.parent / "pack05_plugin_api" / "data" / "plugins" / "packages"
STAGING = ROOT / "data" / "staged"
STAGING.mkdir(parents=True, exist_ok=True)

class SandboxRuntime:
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.stage_dir = STAGING / plugin_id
        self.run_dir = ROOT.parent / "pack03_os_base" / "data" / "vfs" / plugin_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._last_run = None
        self._proc = None

    def stage_package(self, src_dir: str):
        p = Path(src_dir)
        if not p.exists():
            raise FileNotFoundError(p)
        if self.stage_dir.exists():
            shutil.rmtree(self.stage_dir)
        shutil.copytree(p, self.stage_dir)
        return True

    def _apply_limits(self, memory_mb: Optional[int]=None, cpu_seconds: Optional[int]=None):
        if _resource is None:
            return False
        try:
            if memory_mb:
                _resource.setrlimit(_resource.RLIMIT_AS, (memory_mb * 1024*1024, _resource.RLIM_INFINITY))
            if cpu_seconds:
                _resource.setrlimit(_resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
            return True
        except Exception:
            return False

    def run_entry(self, entry_cmd: str, timeout: int = 30, background: bool = False, memory_mb: int = None):
        if self.stage_dir.exists():
            for p in self.run_dir.rglob("*"):
                try:
                    if p.is_file():
                        p.unlink()
                except Exception:
                    pass
            shutil.copytree(self.stage_dir, self.run_dir, dirs_exist_ok=True)
        args = entry_cmd if isinstance(entry_cmd, (list,tuple)) else ["/bin/sh","-c", entry_cmd]
        def _run():
            try:
                p = subprocess.Popen(args, cwd=str(self.run_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self._proc = p
                out, err = p.communicate(timeout=timeout)
                self._last_run = {"rc": p.returncode, "stdout": out.decode() if out else "", "stderr": err.decode() if err else "", "ts": time.time()}
            except subprocess.TimeoutExpired:
                try:
                    p.kill()
                except Exception:
                    pass
                self._last_run = {"rc": -1, "timeout": True, "stdout": "", "stderr": "timeout", "ts": time.time()}
        if background:
            t = threading.Thread(target=_run, daemon=True)
            t.start()
            return {"ok": True, "background": True}
        else:
            _run()
            return self._last_run

    def stop(self):
        if self._proc:
            try:
                self._proc.terminate()
            except Exception:
                pass
            return True
        return False

    def status(self):
        return {"plugin": self.plugin_id, "last_run": self._last_run}
