#!/usr/bin/env python3
"""
Firmware manifest utilities for Aurora .axf format
.manifest.json contains metadata: id, version, target_arch, entrypoints, checksums
"""

import hashlib
from datetime import datetime
from pathlib import Path


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def make_manifest(package_path: Path, meta: dict):
    # meta must include name, version, target_arch
    files = []
    for p in sorted(package_path.rglob("*")):
        if p.is_file():
            rel = p.relative_to(package_path).as_posix()
            files.append({"path": rel, "sha256": sha256(p)})
    manifest = {
        "name": meta.get("name"),
        "version": meta.get("version"),
        "target_arch": meta.get("target_arch"),
        "created": datetime.utcnow().isoformat() + "Z",
        "files": files,
        "meta": meta.get("meta", {}),
    }
    return manifest
