#!/usr/bin/env python3
"""
Long-horizon planner.
- Accepts goals and decomposes into sub-goals via heuristics.
- Uses memory and agent tools to estimate cost and risk.
- Simple rule-based planner available offline; extendable with plugins.
"""

import uuid


class PlanStep:
    def __init__(self, name, action, risk=0.0):
        self.id = str(uuid.uuid4())
        self.name = name
        self.action = action
        self.risk = risk


class Planner:
    def __init__(self, memory=None):
        self.memory = memory

    def decompose(self, goal: str) -> list[PlanStep]:
        # naive decomposition: split by sentences or tokens
        steps = []
        parts = [goal] if len(goal.split(".")) <= 1 else goal.split(".")
        for i, p in enumerate(parts):
            steps.append(
                PlanStep(f"step-{i + 1}", {"type": "execute", "payload": p.strip()}, risk=0.1 * i)
            )
        return steps
