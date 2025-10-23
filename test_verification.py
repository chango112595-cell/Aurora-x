#!/usr/bin/env python3
"""Verification script for T03 adaptive learning."""

import os
import sys
from pathlib import Path

# Add aurora_x to path
sys.path.insert(0, str(Path(__file__).resolve()))

from aurora_x.learn import AdaptiveBiasScheduler, AdaptiveConfig, get_seed_store


def test_seeds_persistence():
    """Test that seeds persist across runs."""
    print("✅ Testing seed persistence...")

    # Create and update seed store
    store1 = get_seed_store()
    store1.update({"seed_key": "test1", "score": 0.8, "success": True})
    store1.save()

    # Load in new instance
    store2 = get_seed_store()
    bias = store2.get_bias("test1")

    if bias != 0.0:
        print(f"  ✓ Seeds persist: bias={bias:.4f}")
        return True
    else:
        print("  ✗ Seeds not persisting")
        return False


def test_determinism():
    """Test deterministic behavior with AURORA_SEED."""
    print("✅ Testing determinism with AURORA_SEED...")

    # Set seed and test
    os.environ["AURORA_SEED"] = "42"

    cfg = AdaptiveConfig(seed=42)
    sched1 = AdaptiveBiasScheduler(cfg)
    sched1.reward("key1", True, magnitude=1.0)
    val1 = sched1.stats["key1"].value

    sched2 = AdaptiveBiasScheduler(cfg)
    sched2.reward("key1", True, magnitude=1.0)
    val2 = sched2.stats["key1"].value

    if val1 == val2:
        print(f"  ✓ Deterministic: both values={val1:.4f}")
        return True
    else:
        print(f"  ✗ Not deterministic: {val1} != {val2}")
        return False


def test_drift_caps():
    """Test that drift doesn't exceed caps."""
    print("✅ Testing drift caps...")

    cfg = AdaptiveConfig(max_drift_per_iter=0.10)
    sched = AdaptiveBiasScheduler(cfg)

    # Simulate long run with extreme inputs
    for i in range(100):
        key = f"key_{i % 5}"
        success = i % 2 == 0
        sched.reward(key, success, magnitude=10.0)  # Large magnitude
        sched.tick()

    # Check no values exceed reasonable bounds
    exceeded = False
    for key, stat in sched.stats.items():
        if abs(stat.value) > 1.0:
            exceeded = True
            print(f"  ✗ Value exceeded bounds: {key}={stat.value}")

    if not exceeded:
        print("  ✓ All values within bounds after 100 iterations")
        # Show sparkline for one key
        sparkline = sched.sparkline("key_0", width=24)
        print(f"  ✓ Sparkline for key_0: {sparkline}")
        return True
    return False


def test_api_endpoints():
    """Test that API endpoint data structures work."""
    print("✅ Testing API data structures...")

    # Create scheduler and generate some data
    sched = AdaptiveBiasScheduler()
    for i in range(10):
        sched.reward(f"key_{i}", i % 2 == 0, magnitude=0.5)
        sched.tick()

    # Test summary
    summary = sched.summary()
    print(f"  ✓ Summary has {len(summary)} entries")

    # Test history
    history = sched.history
    print(f"  ✓ History has {len(history)} entries")

    # Test dump/load
    data = sched.dump()
    print(f"  ✓ Dump has {len(data)} entries")

    return True


if __name__ == "__main__":
    print("=" * 50)
    print("T03 VERIFICATION CHECKLIST")
    print("=" * 50)

    results = []
    results.append(test_seeds_persistence())
    results.append(test_determinism())
    results.append(test_drift_caps())
    results.append(test_api_endpoints())

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All verification checks PASSED!")
    else:
        print("❌ Some checks failed - review above")

    sys.exit(0 if passed == total else 1)
