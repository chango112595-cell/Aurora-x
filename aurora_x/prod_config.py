# Locked production parameters + helper checks
from dataclasses import dataclass


@dataclass(frozen=True)
class ProdConfig:
    EPSILON: float = 0.15
    DECAY: float = 0.98
    COOLDOWN_ITERS: int = 5
    MAX_DRIFT: float = 0.10
    TOP_K: int = 10
    MAX_ABS_DRIFT_BOUND: float = 5.0  # With decay=0.98, max theoretical bound is 0.1/(1-0.98) = 5.0
    SNAPSHOT_DIR: str = ".progress_history"
    SEEDS_PATH: str = ".aurora/seeds.json"


CFG = ProdConfig()


def validate_numbers():
    assert 0.0 <= CFG.EPSILON <= 0.5
    assert 0.9 <= CFG.DECAY <= 1.0
    assert 1 <= CFG.COOLDOWN_ITERS <= 50
    assert 0.01 <= CFG.MAX_DRIFT <= 0.2
    assert 1 <= CFG.TOP_K <= 50
