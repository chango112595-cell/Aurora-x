
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import math
import random

@dataclass
class BiasStat:
    value: float = 0.0
    wins: int = 0
    losses: int = 0
    last_used_iter: int = -1

@dataclass
class AdaptiveConfig:
    epsilon: float = 0.15           # exploration rate
    decay: float = 0.98             # per-iteration decay
    cooldown_iters: int = 5         # don't reboost same bias immediately
    max_drift_per_iter: float = 0.10
    top_k: int = 10
    seed: int = 42

class AdaptiveBiasScheduler:
    """Adaptive scheduler mixing exploitation and ε-greedy exploration."""
    def __init__(self, config: AdaptiveConfig | None = None):
        self.cfg = config or AdaptiveConfig()
        self.rng = random.Random(self.cfg.seed)
        self.iteration = 0
        self.stats: Dict[str, BiasStat] = {}
        self.history: List[Tuple[int, str, float]] = []  # (iter, key, value)

    def load(self, payload: Dict[str, float] | None):
        if not payload: return
        for k, v in payload.items():
            self.stats.setdefault(k, BiasStat()).value = float(v)

    def dump(self) -> Dict[str, float]:
        return {k: round(v.value, 6) for k, v in self.stats.items()}

    def tick(self):
        self.iteration += 1
        for k, st in self.stats.items():
            st.value *= self.cfg.decay
        if len(self.stats) > self.cfg.top_k * 2:
            top = sorted(self.stats.items(), key=lambda kv: abs(kv[1].value), reverse=True)[: self.cfg.top_k]
            self.stats = dict(top)

    def choose(self, candidates: List[str]) -> str:
        if not candidates: return ""
        if self.rng.random() < self.cfg.epsilon:
            return self.rng.choice(candidates)
        best_key, best_val = "", -math.inf
        for k in candidates:
            v = self.stats.get(k, BiasStat()).value
            if v > best_val and (self.iteration - self.stats.get(k, BiasStat()).last_used_iter) >= self.cfg.cooldown_iters:
                best_key, best_val = k, v
        return best_key or self.rng.choice(candidates)

    def reward(self, key: str, success: bool, magnitude: float = 1.0):
        if not key: return
        st = self.stats.setdefault(key, BiasStat())
        st.last_used_iter = self.iteration
        delta = min(self.cfg.max_drift_per_iter, magnitude * 0.1)
        if success:
            st.wins += 1
            st.value += delta
        else:
            st.losses += 1
            st.value -= delta
        self.history.append((self.iteration, key, st.value))

    def summary(self) -> Dict[str, float]:
        return {k: round(v.value, 4) for k, v in sorted(self.stats.items(), key=lambda kv: -abs(kv[1].value))[: self.cfg.top_k]}

    def sparkline(self, key: str, width: int = 24) -> str:
        vals = [v for (it, k, v) in self.history if k == key]
        if not vals: return ""
        mn, mx = min(vals), max(vals)
        span = max(1e-9, mx - mn)
        blocks = '▁▂▃▄▅▆▇█'
        out = []
        for v in vals[-width:]:
            idx = int((v - mn) / span * (len(blocks) - 1))
            out.append(blocks[idx])
        return ''.join(out)
