# FastAPI endpoints for T09 domain router
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from aurora_x.generators.solver import solve_text
from aurora_x.reasoners.units import normalize_to_si, parse_value_with_unit


class SolveRequest(BaseModel):
    problem: str | None = None
    prompt: str | None = None


class UnitRequest(BaseModel):
    value: str


def attach_domain(app: FastAPI):
    @app.post("/api/solve")
    async def api_solve(request: SolveRequest) -> dict[str, Any]:
        """
        Solve a math or physics problem using domain routing.

        Example requests:
        - {"problem": "differentiate 3x^2 + 2x + 5"}
        - {"prompt": "orbital period a=7e6 M=5.972e24"}
        """
        text = (request.problem or request.prompt or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="missing 'problem' or 'prompt'")

        result = solve_text(text)
        if not result.get("ok"):
            raise HTTPException(status_code=422, detail=result)
        return result

    @app.post("/api/explain")
    async def api_explain(request: SolveRequest) -> dict[str, Any]:
        """
        Solve and explain a math or physics problem.

        Returns both the solution and an explanation of what was computed.
        """
        text = (request.problem or request.prompt or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="missing 'problem' or 'prompt'")

        result = solve_text(text)
        if not result.get("ok"):
            raise HTTPException(status_code=422, detail=result)

        keys = ", ".join(sorted(result.keys()))
        return {"ok": True, "explanation": f"Solved offline; fields: {keys}", "result": result}

    @app.post("/api/units")
    async def api_units(request: UnitRequest) -> dict[str, Any]:
        """
        Convert a value with unit to SI units.

        Example requests:
        - {"value": "7000 km"} -> {"si_value": 7000000, "si_unit": "m", "original": "7000 km"}
        - {"value": "5.972e24 kg"} -> {"si_value": 5.972e24, "si_unit": "kg", "original": "5.972e24 kg"}
        - {"value": "1 AU"} -> {"si_value": 149597870700.0, "si_unit": "m", "original": "1 AU"}
        """
        value_str = request.value.strip()
        if not value_str:
            raise HTTPException(status_code=400, detail="missing 'value'")

        # Parse the value and unit
        numeric_value, unit = parse_value_with_unit(value_str)

        if numeric_value is None:
            raise HTTPException(status_code=422, detail=f"Could not parse value from: {value_str}")

        # Normalize to SI
        result = normalize_to_si(numeric_value, unit)

        return {
            "si_value": result["si_value"],
            "si_unit": result["si_unit"],
            "original": value_str,
            "original_value": result["original_value"],
            "original_unit": result["original_unit"],
            "conversion_factor": result["conversion_factor"],
            "unit_type": result["unit_type"],
        }
