#!/usr/bin/env python3
"""
Uplink package tool - sign packages
In production: use PKI / HSM to sign packages. Here we simulate with GPG (recommended).
"""

import json
import subprocess
from pathlib import Path


def sign_package(pkg_path, gpg_key=None):
    # gpg key expected to be loaded already
    out = str(pkg_path) + ".asc"
    cmd = ["gpg", "--armor", "--detach-sign", "-o", out, str(pkg_path)]
    subprocess.check_call(cmd)
    return out


def create_package(commands, outdir="aviation/suggestions"):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    import time

    t = int(time.time())
    p = Path(outdir) / f"flight_pkg_{t}.json"
    p.write_text(json.dumps({"ts": time.time(), "commands": commands}, indent=2))
    return p
