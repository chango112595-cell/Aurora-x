#!/usr/bin/env python3
"""firmware_pack.py - simple packager that wraps a binary into a signed artifact (placeholder)"""

import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--in", dest="fin", required=True)
p.add_argument("--out", dest="fout", required=True)
args = p.parse_args()
fin = Path(args.fin)
fout = Path(args.fout)
if not fin.exists():
    raise SystemExit("input not found")
meta = {"size": fin.stat().st_size, "sha256": hashlib.sha256(fin.read_bytes()).hexdigest()}
fout.write_bytes(fin.read_bytes())
(fout.parent / (fout.name + ".meta.json")).write_text(json.dumps(meta))
print("Packed", fout, "meta written")
