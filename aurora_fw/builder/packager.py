#!/usr/bin/env python3
"""
Creates .axf (Aurora eXecutable Firmware) packages:
- takes folder with firmware files
- generates manifest
- tars content into .axf (gz) and optionally signs with GPG
"""

import json
import subprocess
import tarfile
from pathlib import Path

from .fw_manifest import make_manifest


def create_axf(src_dir: str, out_path: str, meta: dict, gpg_sign: bool = False):
    src = Path(src_dir)
    out = Path(out_path)
    manifest = make_manifest(src, meta)
    mfile = src / ".manifest.json"
    mfile.write_text(json.dumps(manifest, indent=2))
    # create tarball
    with tarfile.open(out, "w:gz") as tf:
        tf.add(src, arcname=".")
    # optionally sign
    if gpg_sign:
        subprocess.check_call(
            ["gpg", "--armor", "--detach-sign", "-o", str(out) + ".asc", str(out)]
        )
    return out


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("src")
    p.add_argument("out")
    p.add_argument("--name", default="aurora-firmware")
    p.add_argument("--version", default="0.0.1")
    p.add_argument("--arch", default="generic")
    p.add_argument("--sign", action="store_true")
    args = p.parse_args()
    meta = {"name": args.name, "version": args.version, "target_arch": args.arch}
    print("Packaging", args.src, "->", args.out)
    create_axf(args.src, args.out, meta, gpg_sign=args.sign)
