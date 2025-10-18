# FastAPI endpoint for human-friendly solver output
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from aurora_x.chat.attach_units_format import _hint, _si_fmt
from aurora_x.generators.solver import solve_text


class PrettyRequest(BaseModel):
    problem: str | None = None
    prompt: str | None = None

def _fmt_seconds(sec: float) -> str:
    if sec < 60:  return f"{sec:.2f} s"
    mins = sec / 60.0
    if mins < 60: return f"{mins:.2f} min"
    hours = mins / 60.0
    if hours < 48: return f"{hours:.2f} hours"
    days = hours / 24.0
    return f"{days:.2f} days"

def attach_pretty(app: FastAPI):
    @app.post("/api/solve/pretty")
    async def api_solve_pretty(request: PrettyRequest) -> dict[str, Any]:
        """
        Solve a problem and return human-friendly formatted output.

        Example: {"problem": "orbital period a=7000 km M=5.972e24 kg"}
        Returns: {"ok": true, "pretty": "Orbital period: 1.60 hours", "result": {...}}
        """
        text = (request.problem or request.prompt or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="missing 'problem' or 'prompt'")

        res = solve_text(text)
        if not res.get("ok"):
            raise HTTPException(status_code=422, detail=res)

        pretty = None
        units_info = []

        if res.get("kind") == "physics.orbital_period":
            sec = float(res["period_s"])
            pretty = f"Orbital period: {_fmt_seconds(sec)}"

            # Add formatted input parameters with SI units and hints
            if "a_m" in res:
                a_fmt = _si_fmt(res["a_m"], "m")
                a_hint = _hint(res["a_m"], "m")
                units_info.append({
                    "parameter": "Semi-major axis",
                    "value": res["a_m"],
                    "unit": "m",
                    "pretty": a_fmt,
                    **({"hint": a_hint} if a_hint else {})
                })

            if "M_kg" in res:
                m_fmt = _si_fmt(res["M_kg"], "kg")
                m_hint = _hint(res["M_kg"], "kg")
                units_info.append({
                    "parameter": "Central mass",
                    "value": res["M_kg"],
                    "unit": "kg",
                    "pretty": m_fmt,
                    **({"hint": m_hint} if m_hint else {})
                })

            # Add period in SI format
            period_fmt = _si_fmt(sec, "s")
            units_info.append({
                "parameter": "Period",
                "value": sec,
                "unit": "s",
                "pretty": period_fmt,
                "human": _fmt_seconds(sec)
            })

        elif res.get("kind") == "physics.em_superposition":
            x,y,z = res["result"]
            pretty = f"Field vector sum: ({x:.3f}, {y:.3f}, {z:.3f})"

            # Format vector components
            for _component, value, label in [(x, "x"), (y, "y"), (z, "z")]:
                units_info.append({
                    "parameter": f"Field {label}-component",
                    "value": value,
                    "unit": "N/C",
                    "pretty": _si_fmt(value, "N/C")
                })

        elif res.get("kind") == "math.evaluate":
            pretty = f"Value = {res['value']:.12g}"
        elif res.get("kind") == "math.differentiate":
            pretty = f"d/dx → {res['derivative']}"

        response = {"ok": True, "pretty": pretty, "result": res}
        if units_info:
            response["units_info"] = units_info

        return response
