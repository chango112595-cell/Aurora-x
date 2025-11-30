#!/usr/bin/env python3
import subprocess, shlex, time
def shell_call(params):
    cmd = params.get("cmd")
    if not cmd:
        raise ValueError("cmd required")
    args = shlex.split(cmd)
    proc = subprocess.run(args, capture_output=True, text=True, timeout=params.get("timeout",30))
    return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "ts": time.time()}
