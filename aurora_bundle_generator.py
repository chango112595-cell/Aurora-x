#!/usr/bin/env python3
# aurora_bundle_generator.py
# Create zip bundles: individual packs, full packs bundle, master OS bundle.

from aurora_build_utils import ROOT, PACKS_DIR, OUT_DIR, safe_write, make_zip, log
from pathlib import Path
import shutil, json, os, textwrap, time

def build_individual_zips(target_packs=None):
    target_packs = target_packs or [d.name for d in PACKS_DIR.iterdir() if d.is_dir()]
    for pack in target_packs:
        p = PACKS_DIR / pack
        if not p.exists(): 
            log(f"Skipping missing pack {pack}")
            continue
        outzip = OUT_DIR / f"{pack}.zip"
        make_zip(p, outzip, strip_base=ROOT)
        log(f"Created zip: {outzip}")

def build_full_bundle():
    bundle = OUT_DIR / "packs_full_bundle.zip"
    temp_dir = OUT_DIR / "tmp_full_bundle"
    if temp_dir.exists(): shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    shutil.copytree(PACKS_DIR, temp_dir / "packs")
    make_zip(temp_dir, bundle, strip_base=OUT_DIR)
    shutil.rmtree(temp_dir)
    log(f"Created full bundle: {bundle}")
    return bundle

def build_master_os_bundle():
    master_dir = OUT_DIR / "tmp_master_os"
    if master_dir.exists(): shutil.rmtree(master_dir)
    master_dir.mkdir(parents=True)
    for d in ("packs", "installer", "tools", "runtime", "manifests"):
        src = ROOT / d
        if src.exists():
            shutil.copytree(src, master_dir / d)
    (master_dir / "README_MASTER.txt").write_text("Aurora OS Master Bundle\nGenerated at: " + time.ctime())
    master_zip = OUT_DIR / "aurora_os_bundle.zip"
    make_zip(master_dir, master_zip, strip_base=master_dir)
    shutil.rmtree(master_dir)
    log(f"Created master OS bundle: {master_zip}")
    return master_zip

if __name__ == "__main__":
    build_individual_zips()
    build_full_bundle()
    build_master_os_bundle()
    log("Bundle generation complete.")
