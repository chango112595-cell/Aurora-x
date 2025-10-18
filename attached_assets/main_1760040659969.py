
# --- Aurora-X main (T03 hooks) ---
from aurora_x.learn.adaptive import AdaptiveBiasScheduler, AdaptiveConfig


def attach_adaptive_scheduler(engine, seed_store):
    cfg = AdaptiveConfig(epsilon=0.15, decay=0.98, cooldown_iters=5, top_k=10)
    sched = AdaptiveBiasScheduler(cfg)
    try:
        sched.load(seed_store.get_biases())
    except Exception:
        pass
    engine._adaptive_scheduler = sched
    return sched
