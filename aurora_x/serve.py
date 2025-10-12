# aurora_x/serve.py — FastAPI app with Aurora-X v3 dashboard mounted
from fastapi import FastAPI, Response, status, HTTPException
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
from aurora_x.chat.attach_task_graph import attach_task_graph
from aurora_x.app_settings import SETTINGS
from aurora_x.generators.solver import solve_text  # Import the solver module
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import time, html
import json
import sys
import subprocess
import traceback
import os

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

# Attach Task Graph visualization for dependency map
attach_task_graph(app)

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

# --- Natural Language Compilation Endpoint ---

class NLCompileRequest(BaseModel):
    """Request model for natural language compilation."""
    prompt: str

class NLCompileResponse(BaseModel):
    """Response model for natural language compilation."""
    run_id: str
    status: str
    files_generated: List[str]
    message: str

@app.post("/api/nl/compile", response_model=NLCompileResponse)
async def compile_from_natural_language(request: NLCompileRequest):
    """
    Process a natural language prompt to generate code.
    
    Args:
        request: JSON body with 'prompt' field containing the natural language request
    
    Returns:
        JSON response with:
        - run_id: the generated run ID
        - status: "success" or "error"
        - files_generated: list of generated file paths
        - message: success or error message
    """
    try:
        from aurora_x.spec.parser_nl import parse_english
        
        prompt = request.prompt.strip()
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Parse the natural language prompt
        parsed = parse_english(prompt)
        
        # Generate timestamp-based run ID
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_name = f"run-{timestamp}"
        runs_dir = Path("runs")
        runs_dir.mkdir(exist_ok=True)
        run_dir = runs_dir / run_name
        
        files_generated = []
        
        # Check if this is a Flask request
        if parsed.get("framework") == "flask":
            # Handle Flask app synthesis
            tools_dir = Path(__file__).parent.parent / "tools"
            sys.path.insert(0, str(tools_dir))
            try:
                from spec_from_flask import create_flask_app_from_text
                app_file = create_flask_app_from_text(prompt, run_dir)
                files_generated.append(str(app_file.relative_to(Path.cwd())))
                
                # Update the latest symlink
                latest = runs_dir / "latest"
                if latest.exists() or latest.is_symlink():
                    latest.unlink()
                latest.symlink_to(run_dir.name)
                
                message = f"Flask application generated successfully at {app_file.name}"
            except ImportError as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to import Flask synthesis module: {str(e)}"
                )
        else:
            # Regular function synthesis
            tools_dir = Path(__file__).parent.parent / "tools"
            sys.path.insert(0, str(tools_dir))
            try:
                from spec_from_text import create_spec_from_text
                
                # Create spec from natural language
                spec_path = create_spec_from_text(prompt, str(Path("specs")))
                files_generated.append(str(spec_path.relative_to(Path.cwd())))
                
                # Compile the generated spec
                comp_script = tools_dir / "spec_compile_v3.py"
                if comp_script.exists():
                    # Run the compilation script
                    result = subprocess.run(
                        [sys.executable, str(comp_script), str(spec_path)],
                        capture_output=True,
                        text=True,
                        env=os.environ.copy()
                    )
                    
                    if result.returncode != 0:
                        error_msg = result.stderr if result.stderr else result.stdout
                        raise HTTPException(
                            status_code=500,
                            detail=f"Spec compilation failed: {error_msg}"
                        )
                    
                    # Parse output to find generated files
                    output_lines = result.stdout.splitlines()
                    for line in output_lines:
                        if "Generated:" in line or "Source:" in line or "Tests:" in line:
                            parts = line.split(":", 1)
                            if len(parts) > 1:
                                path = parts[1].strip()
                                if Path(path).exists():
                                    files_generated.append(str(Path(path).relative_to(Path.cwd())))
                        if "run-" in line:
                            # Extract run ID from output
                            import re
                            match = re.search(r'run-\d{8}-\d{6}', line)
                            if match:
                                run_name = match.group(0)
                    
                    # Update latest symlink
                    if "run-" in run_name:
                        run_dir = runs_dir / run_name
                        if run_dir.exists():
                            latest = runs_dir / "latest"
                            if latest.exists() or latest.is_symlink():
                                latest.unlink()
                            latest.symlink_to(run_dir.name)
                    
                    message = f"Code generated successfully from natural language prompt"
                else:
                    # If no compiler found, just return the spec
                    message = f"Spec generated at {spec_path.name}. Compiler not found for full synthesis."
            except ImportError as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to import synthesis module: {str(e)}"
                )
        
        # Ensure we have valid files generated list
        if not files_generated:
            # Try to find files in the run directory
            if run_dir.exists():
                for item in run_dir.rglob("*"):
                    if item.is_file():
                        files_generated.append(str(item.relative_to(Path.cwd())))
        
        return NLCompileResponse(
            run_id=run_name,
            status="success",
            files_generated=files_generated,
            message=message
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the full traceback for debugging
        error_trace = traceback.format_exc()
        print(f"[ERROR] Natural language compilation failed: {error_trace}", file=sys.stderr)
        
        # Return error response
        return NLCompileResponse(
            run_id="",
            status="error",
            files_generated=[],
            message=f"Failed to process natural language prompt: {str(e)}"
        )

# --- Solver Endpoints ---

class SolverRequest(BaseModel):
    """Request model for the solver endpoints"""
    text: str

@app.post("/api/solve")
async def solve_endpoint(request: SolverRequest):
    """
    Raw solver endpoint that returns the complete solver result
    
    Args:
        request: JSON body with 'text' field containing the problem to solve
    
    Returns:
        JSON response with the raw solver output
    """
    try:
        result = solve_text(request.text)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            content={"ok": False, "error": str(e)},
            status_code=500
        )

@app.post("/api/solve/pretty")
async def solve_pretty_endpoint(request: SolverRequest):
    """
    Pretty solver endpoint that returns formatted human-readable results
    
    Args:
        request: JSON body with 'text' field containing the problem to solve
    
    Returns:
        Plain text response with formatted solution
    """
    try:
        result = solve_text(request.text)
        
        # Format the output in a human-readable way
        if result.get("ok"):
            lines = []
            lines.append("=" * 50)
            lines.append(f"Domain: {result.get('domain', 'unknown')}")
            lines.append(f"Task: {result.get('task', 'unknown')}")
            lines.append("-" * 50)
            
            if result.get("input"):
                lines.append(f"Input: {result['input']}")
            
            if result.get("result"):
                if isinstance(result["result"], dict):
                    lines.append("Result:")
                    for key, value in result["result"].items():
                        if isinstance(value, float):
                            lines.append(f"  {key}: {value:.6f}")
                        else:
                            lines.append(f"  {key}: {value}")
                else:
                    lines.append(f"Result: {result['result']}")
            
            if result.get("explanation"):
                lines.append("")
                lines.append(f"Explanation: {result['explanation']}")
            
            lines.append("=" * 50)
            return PlainTextResponse(content="\n".join(lines))
        else:
            # Error response
            error_msg = f"Error: {result.get('error', 'Unknown error')}"
            if result.get("hint"):
                error_msg += f"\nHint: {result['hint']}"
            return PlainTextResponse(content=error_msg, status_code=400)
            
    except Exception as e:
        return PlainTextResponse(
            content=f"Internal Server Error: {str(e)}",
            status_code=500
        )

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
            "/api/progress",
            "/api/nl/compile"
        ]
    }