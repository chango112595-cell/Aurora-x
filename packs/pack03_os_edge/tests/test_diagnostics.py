#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.diagnostics import collect


def test_collect_snapshot():
    d = collect()
    assert "timestamp" in d
    assert "disk" in d
