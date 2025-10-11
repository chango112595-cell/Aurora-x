from typing import Dict, Any
from aurora_x.router.domain_router import classify_domain
from aurora_x.reasoners import math_core, physics_core

def solve_text(text: str) -> Dict[str, Any]:
    d = classify_domain(text)
    if d.domain == "math":    return math_core.solve(d.task, d.payload)
    if d.domain == "physics": return physics_core.solve(d.task, d.payload)
    return {"ok": False, "err": "domain not implemented", "domain": d.domain, "task": d.task}