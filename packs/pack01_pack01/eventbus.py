#!/usr/bin/env python3
# Simple in-process event bus with a tiny queue and socket hook for future IPC
import queue
import time
from threading import Lock


class EventBus:
    def __init__(self):
        self.q = queue.Queue()
        self.lock = Lock()

    def publish(self, topic, data=None):
        with self.lock:
            self.q.put({"topic": topic, "data": data, "ts": time.time()})

    def poll(self, timeout=0.0):
        try:
            item = self.q.get(timeout=timeout)
            return item
        except Exception:
            return None
