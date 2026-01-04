#!/usr/bin/env python3
import json, shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.ipc_bridge import call_node_script

def test_ipc_roundtrip(tmp_path):
    node = shutil.which("node") or shutil.which("nodejs")
    if not node:
        import pytest; pytest.skip("node not available")
    # Use absolute path from project root with .cjs extension for CommonJS
    js = str(Path(__file__).resolve().parents[1] / "core" / "node_ipc_stub.cjs")
    r = call_node_script(js, {"hello":"world"})
    assert r.get("rc",1) == 0
    assert r.get("resp",{}).get("echo",{}).get("hello") == "world"
