from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

WEIGHTS_FILE = "learn_weights.json"
SEED_BIAS_MIN = 0.0
SEED_BIAS_MAX = 0.5

def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def load(run_root: Path) -> Dict[str, Any]:
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

def save(run_root: Path, weights: Dict[str, Any]) -> None:
    p = Path(run_root) / WEIGHTS_FILE
    p.write_text(json.dumps(weights, indent=2), encoding="utf-8")

def update_seed_bias(current: float, seed_won: bool) -> float:
    """
    Bounded update:
      - success   → +0.05 (up to 0.5)
      - non-win   → -0.02 (down to 0.0)
    """
    if seed_won:
        return _clamp(current + 0.05, SEED_BIAS_MIN, SEED_BIAS_MAX)
    return _clamp(current - 0.02, SEED_BIAS_MIN, SEED_BIAS_MAX)