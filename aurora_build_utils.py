#!/usr/bin/env python3
# aurora_build_utils.py
# Shared utilities for generator scripts

import os
import shutil
import stat
import time
import zipfile
from pathlib import Path

TS = int(time.time())
ROOT = Path.cwd()
PACKS_DIR = ROOT / "packs"
OUT_DIR = ROOT / "pack_zips"
PATCH_DIR = ROOT / "patches"
TESTBENCH_DIR = ROOT / "testbench"
LOG_DIR = ROOT / "gen_logs"
for d in (OUT_DIR, PATCH_DIR, TESTBENCH_DIR, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)


def safe_write(p: Path, content: str, exe=False, backup=True):
    p.parent.mkdir(parents=True, exist_ok=True)
    if backup and p.exists():
        b = p.with_suffix(p.suffix + f".bak.{TS}")
        shutil.copy2(p, b)
    p.write_text(content)
    if exe:
        p.chmod(p.stat().st_mode | stat.S_IEXEC)


def add_to_zip(zf: zipfile.ZipFile, base: Path, strip_base: Path = None):
    if strip_base is None:
        strip_base = base
    for root, dirs, files in os.walk(base):
        for f in files:
            full = Path(root) / f
            rel = full.relative_to(strip_base)
            zf.write(full, rel)


def make_zip(base: Path, outzip: Path, strip_base: Path = None):
    outzip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(outzip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        add_to_zip(zf, base, strip_base or base)


def ensure_packs_dir():
    if not PACKS_DIR.exists():
        raise SystemExit("ERROR: ./packs directory not found. Run from repo root.")


def log(msg):
    print(msg)
    log_file = LOG_DIR / "generator.log"
    existing = log_file.read_text() if log_file.exists() else ""
    log_file.write_text(existing + msg + "\n")
