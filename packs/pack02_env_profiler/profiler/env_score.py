#!/usr/bin/env python3
"""
Score the environment and recommend an execution mode.
Modes:
 - python: run Python-first
 - node: run Node-first
 - hybrid: both
 - portable: restricted
 - embedded: micro-mode
"""

import json
import sys
from pathlib import Path


def score(profile):
    basic = profile.get("basic", {})
    cores = basic.get("cores") or 1
    has_node = basic.get("has_node")
    machine = basic.get("machine", "").lower()
    score = 0
    # CPU weighting
    if cores >= 8:
        score += 30
    elif cores >= 4:
        score += 20
    else:
        score += 10
    # Node availability
    if has_node:
        score += 10
    # arch heuristics
    if "arm" in machine:
        score += 5
    # final decision
    if score >= 35:
        mode = "hybrid"
    elif score >= 25:
        mode = "python"
    else:
        mode = "portable"
    return {"score": score, "recommended_mode": mode}


if __name__ == "__main__":
    path = Path("profile_tmp.json")
    if path.exists():
        p = json.loads(path.read_text())
        print(json.dumps(score(p), indent=2))
    else:
        print(json.dumps({"error": "no profile_tmp.json"}, indent=2))
        sys.exit(1)
