# FastAPI endpoint for human-friendly solver output
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from aurora_x.generators.solver import solve_text

class PrettyRequest(BaseModel):
    problem: Optional[str] = None
    prompt: Optional[str] = None

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
    async def api_solve_pretty(request: PrettyRequest) -> Dict[str, Any]:
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
        if res.get("kind") == "physics.orbital_period":
            sec = float(res["period_s"])
            pretty = f"Orbital period: {_fmt_seconds(sec)}"
        elif res.get("kind") == "physics.em_superposition":
            x,y,z = res["result"]
            pretty = f"Field vector sum: ({x:.3f}, {y:.3f}, {z:.3f})"
        elif res.get("kind") == "math.evaluate":
            pretty = f"Value = {res['value']:.12g}"
        elif res.get("kind") == "math.differentiate":
            pretty = f"d/dx → {res['derivative']}"

        return {"ok": True, "pretty": pretty, "result": res}