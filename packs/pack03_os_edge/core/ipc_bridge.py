#!/usr/bin/env python3
"""
ipc_bridge.py - JSON-over-stdio bridge for python<->node interop.
Pattern:
Python writes JSON lines to node stdin; node writes JSON lines back.
This is intentionally minimal and local-only for pack-level IPC.
"""

import json
import shutil
import subprocess


def call_node_script(js_path: str, payload: dict, timeout=10):
    node = shutil.which("node") or shutil.which("nodejs")
    if not node:
        return {"rc": -1, "error": "node not found"}
    p = subprocess.Popen(
        [node, js_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    inp = json.dumps(payload) + "\n"
    try:
        out, err = p.communicate(inp, timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        return {"rc": -1, "timeout": True}
    try:
        return {
            "rc": p.returncode,
            "resp": json.loads(out.strip()) if out.strip() else None,
            "stderr": err.strip(),
        }
    except Exception:
        return {"rc": p.returncode, "resp_raw": out, "stderr": err.strip()}


if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser()
    p.add_argument("js")
    p.add_argument("--payload", default="{}")
    args = p.parse_args()
    print(call_node_script(args.js, json.loads(args.payload)))
