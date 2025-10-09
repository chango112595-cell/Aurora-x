#!/usr/bin/env python3
"""
Production Configuration for Aurora-X
Pins adaptive learning parameters and provides CI gate checks
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

# Production configuration - DO NOT MODIFY
PROD_CONFIG = {
    "adaptive": {
        "epsilon": 0.15,        # Exploration rate - locked
        "decay": 0.98,          # Per-iteration decay - locked
        "cooldown_iters": 5,    # Cooldown period - locked
        "max_drift_per_iter": 0.10,  # Max drift - locked
        "top_k": 10,            # Top biases to track - locked
        "seed": int(os.environ.get("AURORA_SEED", 42))
    },
    "seeds": {
        "alpha": 0.2,           # EMA smoothing - locked
        "drift_cap": 0.15,      # Drift cap - locked
        "top_n": 10             # Top seeds - locked
    },
    "thresholds": {
        "max_bias": 1.0,        # Maximum allowed bias
        "min_bias": -1.0,       # Minimum allowed bias
        "max_history": 10000,   # Maximum history entries
        "max_test_duration": 60 # Maximum test duration in seconds
    }
}

def validate_config() -> Tuple[bool, str]:
    """Validate production configuration is intact."""
    try:
        # Check adaptive config
        from aurora_x.learn import AdaptiveConfig
        cfg = AdaptiveConfig()
        
        errors = []
        if cfg.epsilon != PROD_CONFIG["adaptive"]["epsilon"]:
            errors.append(f"epsilon mismatch: {cfg.epsilon} != {PROD_CONFIG['adaptive']['epsilon']}")
        if cfg.decay != PROD_CONFIG["adaptive"]["decay"]:
            errors.append(f"decay mismatch: {cfg.decay} != {PROD_CONFIG['adaptive']['decay']}")
        if cfg.cooldown_iters != PROD_CONFIG["adaptive"]["cooldown_iters"]:
            errors.append(f"cooldown mismatch: {cfg.cooldown_iters} != {PROD_CONFIG['adaptive']['cooldown_iters']}")
        
        if errors:
            return False, "\n".join(errors)
        return True, "Configuration validated"
    except Exception as e:
        return False, f"Validation error: {e}"

def ci_gate_check() -> bool:
    """CI gate check for production deployment."""
    print("=" * 60)
    print("AURORA-X PRODUCTION CI GATE CHECK")
    print("=" * 60)
    
    checks_passed = []
    
    # 1. Validate configuration
    print("\n[1/5] Validating production configuration...")
    valid, msg = validate_config()
    if valid:
        print(f"  ✅ {msg}")
        checks_passed.append(True)
    else:
        print(f"  ❌ {msg}")
        checks_passed.append(False)
    
    # 2. Run adaptive tests
    print("\n[2/5] Running adaptive learning tests...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "tests/test_adaptive.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("  ✅ All adaptive tests passed")
            checks_passed.append(True)
        else:
            print(f"  ❌ Adaptive tests failed")
            checks_passed.append(False)
    except Exception as e:
        print(f"  ❌ Test execution failed: {e}")
        checks_passed.append(False)
    
    # 3. Run seed tests
    print("\n[3/5] Running seed persistence tests...")
    try:
        result = subprocess.run(
            [sys.executable, "tests/test_seeds.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("  ✅ All seed tests passed")
            checks_passed.append(True)
        else:
            print(f"  ❌ Seed tests failed")
            checks_passed.append(False)
    except Exception as e:
        print(f"  ❌ Test execution failed: {e}")
        checks_passed.append(False)
    
    # 4. Check drift thresholds
    print("\n[4/5] Checking drift thresholds...")
    try:
        from aurora_x.learn import AdaptiveBiasScheduler, AdaptiveConfig
        
        # Simulate long run
        cfg = AdaptiveConfig(**PROD_CONFIG["adaptive"])
        sched = AdaptiveBiasScheduler(cfg)
        
        for i in range(1000):
            key = f"test_{i % 10}"
            sched.reward(key, i % 2 == 0, magnitude=10.0)
            sched.tick()
        
        # Check all values within bounds
        violations = []
        for key, stat in sched.stats.items():
            if abs(stat.value) > PROD_CONFIG["thresholds"]["max_bias"]:
                violations.append(f"{key}: {stat.value}")
        
        if not violations:
            print(f"  ✅ All biases within ±{PROD_CONFIG['thresholds']['max_bias']} after 1000 iterations")
            checks_passed.append(True)
        else:
            print(f"  ❌ Bias violations: {violations}")
            checks_passed.append(False)
    except Exception as e:
        print(f"  ❌ Drift check failed: {e}")
        checks_passed.append(False)
    
    # 5. Verify determinism
    print("\n[5/5] Verifying deterministic behavior...")
    try:
        from aurora_x.learn import AdaptiveBiasScheduler, AdaptiveConfig
        
        os.environ["AURORA_SEED"] = "12345"
        cfg1 = AdaptiveConfig(seed=12345)
        sched1 = AdaptiveBiasScheduler(cfg1)
        for i in range(10):
            sched1.reward(f"key_{i}", i % 2 == 0, magnitude=0.5)
        val1 = sched1.dump()
        
        cfg2 = AdaptiveConfig(seed=12345)
        sched2 = AdaptiveBiasScheduler(cfg2)
        for i in range(10):
            sched2.reward(f"key_{i}", i % 2 == 0, magnitude=0.5)
        val2 = sched2.dump()
        
        if val1 == val2:
            print("  ✅ Deterministic behavior confirmed")
            checks_passed.append(True)
        else:
            print("  ❌ Non-deterministic behavior detected")
            checks_passed.append(False)
    except Exception as e:
        print(f"  ❌ Determinism check failed: {e}")
        checks_passed.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(checks_passed)
    total = len(checks_passed)
    print(f"CI GATE RESULT: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ PRODUCTION READY - All CI gates passed!")
        return True
    else:
        print("❌ NOT READY - Fix failures above before deploying")
        return False

def save_prod_config():
    """Save production configuration to file."""
    config_path = Path(".aurora/prod_config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(PROD_CONFIG, f, indent=2)
    
    print(f"Production config saved to: {config_path}")

if __name__ == "__main__":
    # Save config
    save_prod_config()
    
    # Run CI gate check
    success = ci_gate_check()
    sys.exit(0 if success else 1)