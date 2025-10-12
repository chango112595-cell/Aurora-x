# aurora_x/serve.py — FastAPI app with Aurora-X v3 dashboard mounted
from fastapi import FastAPI, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pathlib import Path
from aurora_x.serve_dashboard_v2 import make_router
from aurora_x.serve_addons import attach as attach_factory
from aurora_x.chat.attach_router_lang import attach_router
from aurora_x.chat.attach_domain import attach_domain
from aurora_x.chat.attach_pretty import attach_pretty
from aurora_x.chat.attach_format import attach_format
from aurora_x.chat.attach_units_format import attach_units_format
from aurora_x.chat.attach_demo import attach_demo
from aurora_x.chat.attach_demo_runall import attach_demo_runall
from aurora_x.chat.attach_progress import attach_progress
from aurora_x.app_settings import SETTINGS
import time, html

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

# Attach demo cards for testing
attach_demo(app)

# Attach Run All functionality for demo cards
attach_demo_runall(app)

# Attach Progress Dashboard for tracking
attach_progress(app)

@app.get("/dashboard/demos", response_class=HTMLResponse)
async def serve_demo_dashboard():
    """Serve the demo dashboard HTML page"""
    dashboard_path = BASE / "static" / "demo-dashboard.html"
    if dashboard_path.exists():
        return HTMLResponse(content=dashboard_path.read_text())
    else:
        return HTMLResponse(content="<h1>Demo dashboard not found</h1>", status_code=404)

@app.get("/healthz")
def healthz():
    """
    Aurora-X service health endpoint.
    Returns 200 OK with status and component info.
    """
    return {"ok": True, "t08_enabled": SETTINGS.t08_enabled, "ts": time.time()}

# --- UI thresholds (POST to adjust) ---
@app.post("/api/progress/ui_thresholds")
def set_thresholds(payload: dict):
    try:
        ui = payload.get("ui_thresholds", {})
        ok  = int(ui.get("ok", SETTINGS.ui.ok))
        warn= int(ui.get("warn", SETTINGS.ui.warn))
        # clamp
        ok  = max(0, min(100, ok))
        warn= max(0, min(ok, warn))
        SETTINGS.ui.ok   = ok
        SETTINGS.ui.warn = warn
        return {"status":"updated","ui_thresholds":{"ok":ok,"warn":warn}}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

# --- T08 activation (on/off) ---
@app.post("/api/t08/activate")
def t08_activate(payload: dict):
    on = bool(payload.get("on", True))
    SETTINGS.t08_enabled = on
    return {"t08_enabled": SETTINGS.t08_enabled}

# --- Live SVG badge ---
_BADGE_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="170" height="20" role="img" aria-label="progress:{VAL}%">
<linearGradient id="g" x2="0" y2="100%%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient>
<mask id="m"><rect width="170" height="20" rx="3" fill="#fff"/></mask>
<g mask="url(#m)">
  <rect width="90" height="20" fill="#555"/>
  <rect x="90" width="80" height="20" fill="{COLOR}"/>
  <rect width="170" height="20" fill="url(#g)"/>
</g>
<g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
  <text x="45" y="14">aurora progress</text>
  <text x="129" y="14">{VAL}%</text>
</g>
</svg>"""

def _color_for(val:int, ok:int, warn:int)->str:
    if val >= ok: return "#2ebc4f"     # green
    if val >= warn: return "#1f78ff"   # blue
    return "#d73a49"                   # red

@app.get("/badge/progress.svg")
def badge_progress():
    # Get actual progress from progress.json
    import json
    from pathlib import Path
    try:
        progress_path = Path("progress.json")
        if progress_path.exists():
            data = json.loads(progress_path.read_text())
            tasks = data.get("tasks", [])
            total = 0
            for t in tasks:
                percent = t.get("percent", 0)
                if isinstance(percent, str):
                    percent = float(percent.replace('%', ''))
                total += percent
            val = int(round(total / max(1, len(tasks))))
        else:
            val = 85  # default
    except:
        val = 85  # fallback
    
    color = _color_for(val, SETTINGS.ui.ok, SETTINGS.ui.warn)
    svg = _BADGE_TEMPLATE.replace("{VAL}", str(val)).replace("{COLOR}", html.escape(color))
    return Response(content=svg, media_type="image/svg+xml")

@app.get("/")
def root():
    return {
        "ok": True,
        "routes": [
            "/healthz",
            "/dashboard/spec_runs", 
            "/dashboard/demos",
            "/dashboard/progress",
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
            "/api/format/units",
            "/api/demo/cards",
            "/api/progress"
        ]
    }