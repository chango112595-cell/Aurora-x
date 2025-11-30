"""
permissions.py - minimal capability model scaffolding for plugins.
Capabilities are strings like 'network', 'gpu', 'fs-write'.
This module validates requested permissions vs allowed policies.
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "data" / "plugins" / "permissions.json"
POLICY.parent.mkdir(parents=True, exist_ok=True)
if not POLICY.exists():
    POLICY.write_text(json.dumps({"allowed": [], "blocked": []}, indent=2))

def request_permissions(plugin_id: str, perms: list):
    pol = json.loads(POLICY.read_text())
    allowed = []
    blocked = []
    for p in perms:
        if p in pol.get("blocked", []):
            blocked.append(p)
        else:
            allowed.append(p)
    return {"allowed": allowed, "blocked": blocked}
