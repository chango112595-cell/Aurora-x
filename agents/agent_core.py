#!/usr/bin/env python3
"""
Agent Core runtime:
- Agent object with lifecycle (init, plan, act, observe, finish)
- Pluggable tool adapters (shell, python runner, hardware driver)
- Safety hooks and human-in-the-loop gating
"""

import threading, time, uuid, json, traceback
from typing import Any, Dict, List, Callable, Optional
from pathlib import Path

AGENT_RUN_DIR = Path(".agents")
AGENT_RUN_DIR.mkdir(exist_ok=True)

class Tool:
    def __init__(self, name: str, call: Callable[..., Any], meta: Dict=None):
        self.name = name
        self.call = call
        self.meta = meta or {}

class Agent:
    def __init__(self, name: str, memory, tools: Dict[str, Tool], policy: Dict=None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.memory = memory
        self.tools = tools
        self.policy = policy or {"human_in_loop": True, "max_steps": 10}
        self.log = []

    def observe(self, observation: Dict):
        self.memory.write({"agent": self.id, "type":"observation", "payload": observation})
        self.log.append(("observe", observation))

    def plan(self, goal: str) -> List[Dict]:
        # Very simple planner: consult memory and create steps
        ctx = self.memory.search(goal, top_k=3)
        plan = [{"step": i+1, "action": "think", "reason": f"based_on:{r['id'] if 'id' in r else 'mem'}"} for i,r in enumerate(ctx)]
        # add final action attempt
        plan.append({"step": len(plan)+1, "action": "execute", "params": {"goal": goal}})
        self.memory.write({"agent": self.id, "type":"plan", "payload": {"goal":goal, "plan": plan}})
        self.log.append(("plan", plan))
        return plan

    def act(self, step: Dict):
        # Very small dispatcher. Supports tool invocation via policy.
        action = step.get("action")
        if action == "think":
            return {"ok": True, "note": "thinking"}
        if action == "execute":
            params = step.get("params", {})
            # choose best tool
            tool = list(self.tools.values())[0] if self.tools else None
            if not tool:
                return {"ok": False, "error": "no tool available"}
            # human in loop check
            if self.policy.get("human_in_loop", True):
                # store suggestion and require approval (external)
                suggestion = {"agent": self.id, "goal": params.get("goal"), "step": step}
                Path("agents/suggestions").mkdir(parents=True, exist_ok=True)
                fn = Path("agents/suggestions") / f"suggestion_{int(time.time()*1000)}.json"
                fn.write_text(json.dumps(suggestion, indent=2))
                return {"ok": True, "suggestion_saved": str(fn)}
            else:
                try:
                    out = tool.call(params)
                    self.memory.write({"agent": self.id, "type": "action_result", "payload": out})
                    return {"ok": True, "result": out}
                except Exception as e:
                    return {"ok": False, "error": str(e), "trace": traceback.format_exc()}

    def run(self, goal: str):
        steps = self.plan(goal)
        results = []
        for step in steps:
            if len(results) >= self.policy.get("max_steps", 10):
                break
            r = self.act(step)
            results.append(r)
            time.sleep(0.1)
        self.memory.write({"agent": self.id, "type":"run_finished", "payload": {"results": results}})
        return results
