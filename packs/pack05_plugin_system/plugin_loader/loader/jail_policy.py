#!/usr/bin/env python3
"""
jail_policy.py - simple jail policy format and validator.

Policy schema (JSON):
{
  "allowed_paths": ["/allowed/path", ...],
  "blocked_syscalls": ["execve","fork"],
  "max_memory_mb": 256,
  "max_cpu_sec": 10
}

This module only validates and persists policies; it does NOT enforce kernel-level seccomp.
Enforcement is performed by the runtime via soft limits (RLIMIT) and monitoring.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_DIR = ROOT / "data" / "policies"
POLICY_DIR.mkdir(parents=True, exist_ok=True)


def write_policy(name: str, policy: dict):
    p = POLICY_DIR / f"{name}.json"
    p.write_text(json.dumps(policy, indent=2))
    return str(p)


def load_policy(name: str):
    p = POLICY_DIR / f"{name}.json"
    if not p.exists():
        default = {
            "allowed_paths": [str(ROOT / "data" / "staged")],
            "blocked_syscalls": [],
            "max_memory_mb": None,
            "max_cpu_sec": None,
        }
        p.write_text(json.dumps(default, indent=2))
        return default
    return json.loads(p.read_text())


def validate_policy(policy: dict):
    if "allowed_paths" in policy and not isinstance(policy["allowed_paths"], list):
        raise ValueError("allowed_paths must be a list")
    return True
