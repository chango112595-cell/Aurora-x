import os
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from aurora_prototype.modules import MODULES

app = FastAPI(
    title="Aurora Prototype",
    description="Minimal FastAPI prototype with token check and module execution.",
    version="0.1.0",
)

bearer = HTTPBearer(auto_error=True)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> None:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET not set in environment.",
        )
    if credentials.credentials != secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "modules": list(MODULES.keys())}


@app.get("/modules")
def list_modules(token: None = Depends(verify_token)) -> dict[str, Any]:
    return {
        "count": len(MODULES),
        "modules": [
            {"name": m.name, "description": getattr(m, "description", "")} for m in MODULES.values()
        ],
    }


@app.post("/modules/{name}/execute")
def execute_module(
    name: str,
    params: dict[str, Any],
    token: None = Depends(verify_token),
) -> dict[str, Any]:
    module = MODULES.get(name)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")
    try:
        result = module.run(params or {})
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"ok": True, "module": name, "result": result}


def run() -> None:
    import uvicorn

    uvicorn.run(
        "aurora_prototype.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    run()
