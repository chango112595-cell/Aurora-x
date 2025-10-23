# aurora_x/serve_dashboard_v2.py — dashboard router + in-memory log with persistence
try:
    from fastapi import APIRouter, WebSocket
    from fastapi.responses import HTMLResponse, JSONResponse
except Exception:
    APIRouter = None

import json
from pathlib import Path
from typing import Any

spec_runs_memory: list[dict[str, Any]] = []

_LOG = Path("runs/spec_runs.jsonl")
if _LOG.exists():
    try:
        for line in _LOG.read_text(encoding="utf-8").splitlines():
            if line.strip():
                spec_runs_memory.append(json.loads(line))
    except Exception:
        pass


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
        try:
            while True:
                await ws.receive_text()
        except Exception:
            pass

    return router


def record_run(run_id: str, spec: str, ok: bool, report_path: str, bias: float = None, spark: str = None):
    row = {
        "run_id": run_id,
        "spec": spec,
        "ok": ok,
        "report": report_path,
        "bias": bias,
        "spark": spark,
    }
    spec_runs_memory.append(row)
    try:
        _LOG.parent.mkdir(parents=True, exist_ok=True)
        with _LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass
