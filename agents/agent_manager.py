#!/usr/bin/env python3
"""
Agent manager: create, run, schedule agents; simple thread-pool
"""

import queue
import threading
from pathlib import Path

from .agent_core import Agent

AGENTS_DIR = Path(".agents")
AGENTS_DIR.mkdir(exist_ok=True)


class AgentManager:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.queue = queue.Queue()
        self.workers = []
        self.running = False

    def start(self):
        self.running = True
        for i in range(self.max_workers):
            t = threading.Thread(target=self._worker_loop, daemon=True, name=f"agent-worker-{i}")
            t.start()
            self.workers.append(t)

    def _worker_loop(self):
        while self.running:
            task = self.queue.get()
            if task is None:
                break
            agent, goal, cb = task
            try:
                res = agent.run(goal)
                if cb:
                    cb(res)
            except Exception as e:
                print("agent error", e)
            self.queue.task_done()

    def submit(self, agent: Agent, goal: str, cb=None):
        self.queue.put((agent, goal, cb))

    def stop(self):
        self.running = False
        for _ in self.workers:
            self.queue.put(None)
