import asyncio
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aurora_nexus_v3.core.hybrid_orchestrator import HybridOrchestrator

APP_TOKEN = os.environ.get("AURORA_API_TOKEN", None)

app = FastAPI(title="Aurora Nexus v3 (prototype)")
orchestrator = HybridOrchestrator()


class ExecRequest(BaseModel):
    module: str
    action: str
    payload: dict = {}


@app.on_event("startup")
async def startup():
    ok = await orchestrator.initialize()
    if not ok:
        raise RuntimeError("Failed to initialize orchestrator")


@app.on_event("shutdown")
async def shutdown():
    await orchestrator.shutdown()


def require_token(token: str):
    if APP_TOKEN and token != APP_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/health")
async def health():
    return {"ok": True, "version": orchestrator.get_status().get("version")}


@app.get("/status")
async def status():
    return orchestrator.get_status()


@app.get("/modules")
async def modules():
    return {"modules": ["temperature_sensor", "device_manager", "logger_adapter"]}


@app.post("/execute")
async def execute(req: ExecRequest, token: str = None):
    require_token(token)
    if req.module == "temperature_sensor" and req.action == "read":
        val = orchestrator.temperature_sensor.read()
        return {"value": val}
    if req.module == "device_manager" and req.action == "register":
        device_id = req.payload.get("device_id")
        if not device_id:
            raise HTTPException(400, "device_id required")
        ok = orchestrator.device_manager.register(device_id)
        return {"registered": ok}
    raise HTTPException(404, "module/action not found")
