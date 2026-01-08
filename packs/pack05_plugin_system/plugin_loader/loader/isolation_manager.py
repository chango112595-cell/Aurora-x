#!/usr/bin/env python3
"""
isolation_manager.py - manages staging and simple isolation tasks.

Responsibilities:
- Accept plugin package paths and coordinate staging (calls PACK05 API loader)
- Validate package via manifest
- Optionally set resource governor hints (writes config files)
- Provides safe API for Supervisor to ask for run requests (creates request files consumed by sandbox_host)
"""

import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pack05_plugin_api"))
from core.registry import PluginRegistry as _PR

ROOT = Path(__file__).resolve().parents[1]
STAGE_BASE = ROOT / "data" / "staged"
STAGE_BASE.mkdir(parents=True, exist_ok=True)
REQ_DIR = ROOT / "data" / "requests"
REQ_DIR.mkdir(parents=True, exist_ok=True)


class IsolationManager:
    def __init__(self):
        self.registry = _PR()

    def stage_plugin(self, package_dir: str):
        p = Path(package_dir)
        if not p.exists():
            raise FileNotFoundError(p)
        pid = p.name
        target = STAGE_BASE / pid
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(p, target)
        return str(target)

    def request_run(self, plugin_id: str, cmd: str, timeout: int = 10):
        req = {"plugin": plugin_id, "cmd": cmd, "timeout": timeout}
        fname = f"{plugin_id}-{int(time.time() * 1000)}.req"
        (REQ_DIR / fname).write_text(json.dumps(req))
        return str(REQ_DIR / fname)
