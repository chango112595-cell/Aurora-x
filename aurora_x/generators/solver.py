from typing import Dict, Any
from aurora_x.router.domain_router import classify_domain
from aurora_x.reasoners import math_core, physics_core
from aurora_x.utils.units import extract_quantities, normalize_payload

def solve_text(text: str) -> Dict[str, Any]:
    d = classify_domain(text)
    if d.domain == "math":
        return math_core.solve(d.task, d.payload)

    if d.domain == "physics":
        # 1) Pull inline quantities from free text (a=..., M=..., with units)
        si_from_text = extract_quantities(text)
        # 2) Respect any JSON-style payload too (normalize to SI)
        si_from_payload = normalize_payload(d.payload) if isinstance(d.payload, dict) else {}
        payload = {**d.payload, **si_from_text, **si_from_payload}

        # Ensure canonical keys for physics_core
        if "a_m" in payload: payload.setdefault("semi_major_axis_m", payload["a_m"])
        if "M_kg" in payload: payload.setdefault("mass_central_kg", payload["M_kg"])

        return physics_core.solve(d.task, payload)

    return {"ok": False, "err": "domain not implemented", "domain": d.domain, "task": d.task}