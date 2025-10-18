from __future__ import annotations

import math
from typing import Any

G = 6.67430e-11  # m^3 kg^-1 s^-2


def orbital_period(semi_major_axis_m: float, mass_central_kg: float) -> float:
    if semi_major_axis_m <= 0 or mass_central_kg <= 0:
        raise ValueError("a and M must be positive")
    return 2.0 * math.pi * math.sqrt((semi_major_axis_m**3) / (G * mass_central_kg))


def em_superposition(field_vectors: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    return (sum(v[0] for v in field_vectors), sum(v[1] for v in field_vectors), sum(v[2] for v in field_vectors))


def solve(intent: str, payload: dict[str, Any]) -> dict[str, Any]:
    if intent == "orbital_period":
        a = float(payload.get("a_m") or payload.get("a") or payload.get("semi_major_axis_m") or 0.0)
        M = float(payload.get("M_kg") or payload.get("M") or payload.get("mass_central_kg") or 0.0)
        try:
            period = orbital_period(a, M)
            return {"ok": True, "kind": "physics.orbital_period", "a_m": a, "M_kg": M, "period_s": period}
        except ValueError as e:
            return {"ok": False, "err": str(e)}
    if intent == "em_superposition":
        vecs = payload.get("vectors") or payload.get("field_vectors") or []
        vecs_t = [tuple(map(float, v)) for v in vecs]
        return {"ok": True, "kind": "physics.em_superposition", "result": em_superposition(vecs_t)}
    return {"ok": False, "err": f"unknown physics intent: {intent}"}
