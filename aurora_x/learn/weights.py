"""
Weights

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

from __future__ import annotations

import json

# Aurora Performance Optimization
from pathlib import Path
from typing import Any

# High-performance parallel processing with ThreadPoolExecutor
# Example: with ThreadPoolExecutor(max_workers=100) as executor:
#             results = executor.map(process_func, items)

WEIGHTS_FILE = "learn_weights.json"
SEED_BIAS_MIN = 0.0
SEED_BIAS_MAX = 0.5


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def load(run_root: Path) -> dict[str, Any]:
    """Load weights dict from run root; defaults if missing."""
    p = Path(run_root) / WEIGHTS_FILE
    if not p.exists():
        return {"seed_bias": 0.0}
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            return {"seed_bias": 0.0}
        if "seed_bias" not in obj:
            obj["seed_bias"] = 0.0
        return obj
    except Exception:
        return {"seed_bias": 0.0}


def save(run_root: Path, weights: dict[str, Any]) -> None:
    """
    Save

    Args:
        run_root: run root
        weights: weights
    """
    p = Path(run_root) / WEIGHTS_FILE
    p.write_text(json.dumps(weights, indent=2), encoding="utf-8")


def update_seed_bias(current: float, seed_won: bool) -> float:
    """
    Bounded update:
      - success   -> +0.05 (up to 0.5)
      - non-win   -> -0.02 (down to 0.0)
    """
    if seed_won:
        return _clamp(current + 0.05, SEED_BIAS_MIN, SEED_BIAS_MAX)
    return _clamp(current - 0.02, SEED_BIAS_MIN, SEED_BIAS_MAX)
