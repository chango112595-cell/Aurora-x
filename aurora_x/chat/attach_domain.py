# FastAPI endpoints for T09 domain router
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from aurora_x.generators.solver import solve_text

class SolveRequest(BaseModel):
    problem: Optional[str] = None
    prompt: Optional[str] = None

def attach_domain(app: FastAPI):
    @app.post('/api/solve')
    async def api_solve(request: SolveRequest) -> Dict[str, Any]:
        """
        Solve a math or physics problem using domain routing.
        
        Example requests:
        - {"problem": "differentiate 3x^2 + 2x + 5"}
        - {"prompt": "orbital period a=7e6 M=5.972e24"}
        """
        text = (request.problem or request.prompt or '').strip()
        if not text:
            raise HTTPException(status_code=400, detail="missing 'problem' or 'prompt'")
        
        result = solve_text(text)
        if not result.get("ok"):
            raise HTTPException(status_code=422, detail=result)
        return result

    @app.post('/api/explain')
    async def api_explain(request: SolveRequest) -> Dict[str, Any]:
        """
        Solve and explain a math or physics problem.
        
        Returns both the solution and an explanation of what was computed.
        """
        text = (request.problem or request.prompt or '').strip()
        if not text:
            raise HTTPException(status_code=400, detail="missing 'problem' or 'prompt'")
        
        result = solve_text(text)
        if not result.get("ok"):
            raise HTTPException(status_code=422, detail=result)
        
        keys = ", ".join(sorted(result.keys()))
        return {"ok": True, "explanation": f"Solved offline; fields: {keys}", "result": result}