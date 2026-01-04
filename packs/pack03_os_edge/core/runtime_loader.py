#!/usr/bin/env python3
"""
runtime_loader.py - Multi-runtime manager (Python / Node)

Responsibilities:
- Query PACK 2 profile (live/environment/profile.json) to choose runtime
- Launch runtime processes via ProcessAbstraction / Sandbox
- Provide API: choose_runtime(), run_script(), run_module()
"""
import json, shutil, subprocess, os
from pathlib import Path
from .process_abstraction import PackProcess
from .hypervisor import Hypervisor

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT.parents[0] / "live" / "environment" / "profile.json"

def load_profile():
    if PROFILE.exists():
        return json.loads(PROFILE.read_text())
    return {}

class RuntimeLoader:
    def __init__(self, pack_id: str):
        self.pack_id = pack_id
        self.hv = Hypervisor()
        self.proc = self.hv.create_instance(pack_id).process

    def choose_runtime(self):
        p = load_profile()
        mode = p.get("summary",{}).get("recommended_mode", "python")
        # fallback heuristics
        if mode == "hybrid" and not shutil.which("node"):
            mode = "python"
        return mode

    def run_python(self, module_or_script, timeout=30):
        cmd = f"python3 {module_or_script}"
        return self.hv.run_in(self.pack_id, cmd, timeout=timeout)

    def run_node(self, script, timeout=30):
        node_bin = shutil.which("node") or shutil.which("nodejs")
        if not node_bin:
            return {"rc": -1, "stderr": "node not found"}
        cmd = f"{node_bin} {script}"
        return self.hv.run_in(self.pack_id, cmd, timeout=timeout)

    def run(self, target, timeout=30, prefer=None):
        runtime = prefer or self.choose_runtime()
        if runtime == "python":
            return self.run_python(target, timeout=timeout)
        elif runtime == "node":
            return self.run_node(target, timeout=timeout)
        else:
            # hybrid -> try python then node
            r = self.run_python(target, timeout=timeout)
            if r.get("rc",1) != 0:
                return self.run_node(target, timeout=timeout)
            return r

if __name__=="__main__":
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("pack")
    p.add_argument("target")
    args = p.parse_args()
    rl = RuntimeLoader(args.pack)
    print(json.dumps(rl.run(args.target), indent=2))
