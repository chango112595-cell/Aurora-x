#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--in",dest="fin",required=True)
p.add_argument("--out",dest="fout",required=True)
a=p.parse_args()
b=Path(a.fin).read_bytes()
h=hashlib.sha256(b).hexdigest()
Path(a.fout).write_text(json.dumps({"file":a.fin,"sha256":h}))
print("signed")