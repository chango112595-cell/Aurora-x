
from aurora_x.learn.adaptive import AdaptiveBiasScheduler, AdaptiveConfig

def test_exploit_choice():
    cfg = AdaptiveConfig(epsilon=0.0, decay=1.0, cooldown_iters=0, seed=1)
    s = AdaptiveBiasScheduler(cfg)
    s.stats['a'] = type('S', (), {'value':1.0,'wins':0,'losses':0,'last_used_iter':-1})()
    s.stats['b'] = type('S', (), {'value':0.1,'wins':0,'losses':0,'last_used_iter':-1})()
    assert s.choose(['a','b']) == 'a'

def test_decay_applies():
    s = AdaptiveBiasScheduler()
    s.reward('x', True, magnitude=1.0)
    v1 = s.stats['x'].value
    s.tick()
    assert s.stats['x'].value < v1
