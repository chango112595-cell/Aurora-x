# aurora_x/serve.py — FastAPI app with Aurora-X v3 dashboard mounted
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from aurora_x.serve_dashboard_v2 import make_router

BASE = Path(__file__).parent
app = FastAPI(title="Aurora-X Ultra v3")

app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
app.include_router(make_router(BASE / "static", BASE / "templates"))

@app.get("/")
def root():
    return {
        "ok": True,
        "routes": ["/dashboard/spec_runs", "/api/spec_runs", "/ws/spec_updates"]
    }
