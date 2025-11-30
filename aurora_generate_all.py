#!/usr/bin/env python3
# aurora_generate_all.py
# Main driver - orchestrates generation, patch creation, bundle creation, and testbench.

import argparse, subprocess, sys, os
from aurora_build_utils import log, OUT_DIR, PATCH_DIR, TESTBENCH_DIR
from pathlib import Path

def run(cmd):
    print("> " + cmd)
    return subprocess.run(cmd, shell=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Run full generator (packs, patches, bundles, testbench)")
    parser.add_argument("--packs", type=str, help="Comma or dash separated packs to (e.g. 5-15 or 06,07)")
    args = parser.parse_args()

    print("Step 1: regenerating packs (if necessary) - skipped (packs should exist from prior generator).")

    print("Step 2: producing patches")
    run("python3 aurora_patch_generator.py")

    print("Step 3: producing bundles")
    run("python3 aurora_bundle_generator.py")

    print("Step 4: producing testbench")
    run("python3 aurora_testbench_generator.py")

    print("All generation steps complete. Zips in pack_zips/, patches in patches/, testbench in testbench/")

if __name__ == '__main__':
    main()
