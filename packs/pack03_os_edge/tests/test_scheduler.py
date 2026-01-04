import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.scheduler import Scheduler

def test_scheduler_runs_task():
    s = Scheduler()
    results = []
    def f():
        results.append(1)
    s.start()
    s.schedule(0.01, f)
    time.sleep(0.05)
    s.stop()
    assert len(results) == 1
