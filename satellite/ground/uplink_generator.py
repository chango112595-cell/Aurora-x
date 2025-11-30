#!/usr/bin/env python3
"""
Generate signed uplink packages for satellites.
- Package contains commands + metadata + required validation signatures
- Human operator MUST sign package using GPG or HSM
"""

import json, time, subprocess, sys
from pathlib import Path

def create_package(commands, outdir="satellite/packages"):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    p = Path(outdir) / f"uplink_{ts}.json"
    p.write_text(json.dumps({"ts":time.time(),"commands":commands}, indent=2))
    return p

def sign_package(path):
    subprocess.check_call(["gpg","--armor","--detach-sign", str(path)])
    return str(path)+".asc"

if __name__=="__main__":
    pkg = create_package([{"cmd":"status"}])
    print("Created",pkg)
    print("Sign with gpg --detach-sign",pkg)
