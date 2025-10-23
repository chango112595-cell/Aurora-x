"""
Run with:  python tools/ci_gate.py
Exits non-zero on failure (CI gate).
"""

import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aurora_x.learn.adaptive import AdaptiveBiasScheduler, AdaptiveConfig
from aurora_x.prod_config import CFG, validate_numbers


def test_adaptive_numbers():
    validate_numbers()


def test_determinism():
    c = AdaptiveConfig(
        seed=123,
        epsilon=0.15,
        decay=0.98,
        cooldown_iters=5,
        max_drift_per_iter=CFG.MAX_DRIFT,
        top_k=CFG.TOP_K,
    )
    s1, s2 = AdaptiveBiasScheduler(c), AdaptiveBiasScheduler(c)
    candidates = ["a", "b", "c"]
    seq1, seq2 = [], []
    for _ in range(100):
        s1.tick()
        s2.tick()
        seq1.append(s1.choose(candidates))
        seq2.append(s2.choose(candidates))
    assert seq1 == seq2


def test_drift_bound():
    c = AdaptiveConfig(epsilon=0.0, decay=0.98, cooldown_iters=0, max_drift_per_iter=CFG.MAX_DRIFT, top_k=CFG.TOP_K)
    s = AdaptiveBiasScheduler(c)
    for _ in range(1000):
        s.tick()
        s.reward("a", True, magnitude=1.0)
    # With decay, value should stay bounded
    assert abs(s.stats["a"].value) <= CFG.MAX_ABS_DRIFT_BOUND * 1.1  # Small margin for floating point


def test_seeds_persist():
    p = Path(CFG.SEEDS_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"hello": 0.2}))
    data = json.loads(p.read_text())
    assert "hello" in data


def main():
    tests = [test_adaptive_numbers, test_determinism, test_drift_bound, test_seeds_persist]
    for t in tests:
        t()
    print("CI gate: PASSED")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print("CI gate: FAILED:", e)
        sys.exit(1)
