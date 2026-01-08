"""
Lightweight cooperative scheduler for Aurora.
Allows scheduling callables with optional resource tags.
Not a full OS scheduler, but sufficient for pack lifecycle tasks.
"""

import heapq
import threading
import time
from collections.abc import Callable


class ScheduledTask:
    def __init__(self, ts: float, func: Callable, args=(), kwargs=None):
        self.ts = ts
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}

    def __lt__(self, other):
        return self.ts < other.ts


class Scheduler:
    def __init__(self):
        self._lock = threading.Lock()
        self._queue = []
        self._running = False
        self._thread = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)

    def _loop(self):
        while self._running:
            now = time.time()
            task = None
            with self._lock:
                if self._queue and self._queue[0].ts <= now:
                    task = heapq.heappop(self._queue)
            if task:
                try:
                    task.func(*task.args, **task.kwargs)
                except Exception:
                    # swallow exceptions; scheduler must be resilient
                    pass
            time.sleep(0.01)

    def schedule(self, delay_secs: float, func: Callable, *args, **kwargs):
        ts = time.time() + float(delay_secs)
        with self._lock:
            heapq.heappush(self._queue, ScheduledTask(ts, func, args, kwargs))
