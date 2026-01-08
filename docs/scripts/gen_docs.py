#!/usr/bin/env python3
import glob
import os

import yaml

out = "docs/docs/packs"
os.makedirs(out, exist_ok=True)
for m in glob.glob("packs/*/manifest.yaml"):
    name = os.path.basename(os.path.dirname(m))
    try:
        data = yaml.safe_load(open(m))
        t = data["pack"]["name"]
    except:
        t = name
    open(f"{out}/{name}.md", "w").write(f"# {t}\n\nGenerated doc for {name}\n")
print("docs OK")
