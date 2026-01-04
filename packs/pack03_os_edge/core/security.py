#!/usr/bin/env python3
"""
security.py - policy loader and hints for sandboxing

Design:
- Provide a JSON policy format for allowed syscalls / files / caps
- Provide helper to detect AppArmor/SELinux presence
- Provide a no-op safe fallback on unsupported env
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY_DIR = ROOT / "data" / "security"
POLICY_DIR.mkdir(parents=True, exist_ok=True)


def detect_mandatory_access_control():
    if shutil.which("aa-status"):
        return "apparmor"
    # selinux check
    try:
        with open("/sys/fs/selinux/enforce") as f:
            if f.read().strip() in ("1", "0"):
                return "selinux"
    except Exception:
        pass
    return None


def load_policy(name="default"):
    p = POLICY_DIR / f"{name}.json"
    if p.exists():
        return json.loads(p.read_text())
    # default safe policy
    pol = {
        "allow_network": False,
        "allow_exec": True,
        "allowed_paths": [str(ROOT / "data" / "vfs")],
    }
    p.write_text(json.dumps(pol, indent=2))
    return pol


def check_path_allowed(path):
    pol = load_policy()
    for base in pol.get("allowed_paths", []):
        if str(path).startswith(base):
            return True
    return False


if __name__ == "__main__":
    print(detect_mandatory_access_control())
    print(load_policy())
