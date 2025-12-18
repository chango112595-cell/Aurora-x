#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path

ROOT = Path.cwd()
packs = sorted([p for p in (ROOT/"packs").iterdir() 
                if p.is_dir() and p.name.startswith("pack") and (p/"tests").exists()])

fails = []
for p in packs:
    print(f"\n=== TEST {p.name} ===")
    rc = subprocess.run([sys.executable,"-m","pytest",str(p/"tests"),"-q","--no-cov"]).returncode
    if rc != 0:
        fails.append(p.name)

if fails:
    print("\nFAILED:", fails)
    sys.exit(1)
print("\nALL PACKS OK")