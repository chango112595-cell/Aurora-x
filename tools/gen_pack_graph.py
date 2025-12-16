#!/usr/bin/env python3
from pathlib import Path
import yaml

lines=["digraph packs {"]
for p in Path("packs").glob("*"):
    m = p/"manifest.yaml"
    if not m.exists(): continue
    name=p.name
    lines.append(f'"{name}";')
    try:
        data=yaml.safe_load(open(m))
        deps=data.get("pack",{}).get("dependencies",[])
        for d in deps:
            lines.append(f'"{name}" -> "{d.get("pack_id")}";')
    except: pass
lines.append("}")
open("tools/pack_graph.dot","w").write("\n".join(lines))
print("ok")