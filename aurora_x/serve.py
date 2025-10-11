# aurora_x/serve.py — FastAPI app with Aurora-X v3 dashboard mounted
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from aurora_x.serve_dashboard_v2 import make_router
from aurora_x.serve_addons import attach as attach_factory
from aurora_x.chat.attach_router_lang import attach_router
from aurora_x.chat.attach_domain import attach_domain
from aurora_x.chat.attach_pretty import attach_pretty
from aurora_x.chat.attach_format import attach_format
from aurora_x.chat.attach_units_format import attach_units_format

BASE = Path(__file__).parent
app = FastAPI(title="Aurora-X Ultra v3")

# Create static and templates directories if they don't exist
static_dir = BASE / "static"
templates_dir = BASE / "templates"
static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

# Only mount static if directory exists and has content
if static_dir.exists() and any(static_dir.iterdir()):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include dashboard router
app.include_router(make_router(static_dir, templates_dir))

# Attach English mode addons
attach_factory(app)

# Attach T08 Intent Router for /chat endpoint
attach_router(app)

# Attach T09 Domain Router for /api/solve and /api/explain endpoints
attach_domain(app)

# Attach Pretty formatter for human-friendly output
attach_pretty(app)

# Attach seconds formatter for time conversion
attach_format(app)

# Attach units formatter with SI prefixes and hints
attach_units_format(app)

@app.get("/healthz")
async def healthz():
    """
    Aurora-X service health endpoint.
    Returns 200 OK with status and component info.
    """
    return {
        "status": "ok",
        "service": "Aurora-X",
        "version": "v3",
        "components": {
            "router": "active",
            "synthesis": "ready",
            "learning_engine": "online"
        }
    }

@app.get("/")
def root():
    return {
        "ok": True,
        "routes": [
            "/healthz",
            "/dashboard/spec_runs", 
            "/api/spec_runs", 
            "/ws/spec_updates",
            "/api/chat",
            "/api/approve",
            "/api/english/status",
            "/chat",
            "/api/solve",
            "/api/explain",
            "/api/solve/pretty",
            "/api/units",
            "/api/format/seconds",
            "/api/format/units"
        ]
    }