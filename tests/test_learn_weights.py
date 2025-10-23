from __future__ import annotations

import tempfile
from pathlib import Path

from aurora_x.learn import weights as w


def test_update_seed_bias_bounds_and_steps():
    assert w.update_seed_bias(0.0, True) == 0.05
    assert w.update_seed_bias(0.49, True) == 0.5
    assert w.update_seed_bias(0.5, False) == 0.48
    assert w.update_seed_bias(0.0, False) == 0.0


def test_persist_load_cycle():
    root = Path(tempfile.mkdtemp())
    data = {"seed_bias": 0.12}
    w.save(root, data)
    got = w.load(root)
    assert got["seed_bias"] == 0.12
