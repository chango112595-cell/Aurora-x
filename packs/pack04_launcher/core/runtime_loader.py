#!/usr/bin/env python3
"""
runtime_loader.py - Local multi-runtime manager for pack04.
Queries environment profile and launches runtimes accordingly.
"""
import json, shutil
from pathlib import Path
from .process_abstraction import PackProcess

ROOT = Path(__file__).resolve().parents[1]
PROFILE = Path("live") / "environment" / "profile.json"

def load_profile():
    if PROFILE.exists():
        return json.loads(PROFILE.read_text())
    return {}

class RuntimeLoader:
    def __init__(self, pack_id: str = "pack04_launcher"):
        self.pack_id = pack_id
        self.proc = PackProcess(pack_id)

    def choose_runtime(self):
        p = load_profile()
        mode = p.get("summary", {}).get("recommended_mode", "python")
        if mode == "hybrid" and not shutil.which("node"):
            mode = "python"
        return mode

    def run_python(self, module_or_script, timeout=30):
        cmd = f"python3 {module_or_script}"
        return self.proc.run(cmd, timeout=timeout)

    def run_node(self, script, timeout=30):
        node_bin = shutil.which("node") or shutil.which("nodejs")
        if not node_bin:
            return {"rc": -1, "stderr": "node not found"}
        cmd = f"{node_bin} {script}"
        return self.proc.run(cmd, timeout=timeout)

    def run(self, target, timeout=30, prefer=None):
        runtime = prefer or self.choose_runtime()
        if runtime == "python":
            return self.run_python(target, timeout=timeout)
        elif runtime == "node":
            return self.run_node(target, timeout=timeout)
        else:
            r = self.run_python(target, timeout=timeout)
            if r.get("rc", 1) != 0:
                return self.run_node(target, timeout=timeout)
            return r
