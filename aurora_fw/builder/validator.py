#!/usr/bin/env python3
"""
Validator for .axf packages: checks manifest integrity and optional GPG signature
"""

import json
import subprocess
import tarfile
from pathlib import Path

from .fw_manifest import sha256


def verify_axf(axf_path: str):
    p = Path(axf_path)
    if not p.exists():
        raise FileNotFoundError(axf_path)
    # if signature exists, verify it
    asc = p.with_suffix(p.suffix + ".asc")
    if asc.exists():
        try:
            subprocess.check_call(["gpg", "--verify", str(asc), str(p)])
        except subprocess.CalledProcessError:
            return False, "gpg verify failed"
    # extract manifest from tar to temp
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(p, "r:*") as tf:
            tf.extractall(tmp)
        mf = Path(tmp) / ".manifest.json"
        if not mf.exists():
            return False, "manifest missing"
        manifest = json.loads(mf.read_text())
        # check each file checksum
        for f in manifest.get("files", []):
            fp = Path(tmp) / f["path"]
            if not fp.exists():
                return False, f"file missing: {f['path']}"
            if sha256(fp) != f["sha256"]:
                return False, f"checksum mismatch {f['path']}"
    return True, "ok"
