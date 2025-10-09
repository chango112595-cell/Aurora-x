try:
    from fastapi import APIRouter, WebSocket
    from fastapi.responses import HTMLResponse, JSONResponse
except Exception:
    APIRouter = None

from pathlib import Path
from typing import List, Dict, Any

spec_runs_memory: List[Dict[str, Any]] = []

def make_router(static_dir: Path, templates_dir: Path):
    router = APIRouter()

    @router.get("/dashboard/spec_runs")
    def dashboard_page():
        html = (templates_dir / "spec_runs.html").read_text(encoding="utf-8")
        return HTMLResponse(html)

    @router.get("/api/spec_runs")
    def spec_runs():
        return JSONResponse({"runs": spec_runs_memory[-50:]})

    @router.websocket("/ws/spec_updates")
    async def ws_updates(ws: WebSocket):
        await ws.accept()
        # keepalive; page will poll via /api/spec_runs
        try:
            while True:
                await ws.receive_text()
        except Exception:
            pass

    return router

def record_run(run_id: str, spec: str, ok: bool, report_path: str, bias: float | None = None, spark: str | None = None):
    spec_runs_memory.append({
        "run_id": run_id, "spec": spec, "ok": ok, "report": report_path, "bias": bias, "spark": spark
    })