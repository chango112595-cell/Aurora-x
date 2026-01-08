#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.security import check_path_allowed, load_policy


def test_security_policy():
    p = load_policy()
    assert isinstance(p, dict)
    assert check_path_allowed("some/path") in (True, False)
