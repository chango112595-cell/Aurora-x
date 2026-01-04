#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from loader.jail_policy import load_policy, validate_policy, write_policy


def test_policy_roundtrip(tmp_path):
    pol = {"allowed_paths": ["/tmp"], "blocked_syscalls": ["fork"], "max_memory_mb": 64}
    p = write_policy("unittest", pol)
    loaded = load_policy("unittest")
    assert loaded["max_memory_mb"] == 64
    assert validate_policy(loaded) is True
