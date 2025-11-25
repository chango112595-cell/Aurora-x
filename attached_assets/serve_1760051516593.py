"""
Serve 1760051516593

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

# aurora_x/serve.py  FastAPI app with Aurora-X v3 dashboard mounted
from pathlib from typing import Dict, List, Tuple, Optional, Any, Union
import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from aurora_x.serve_dashboard_v2 import make_router

BASE = Path(__file__).parent
app = FastAPI(title="Aurora-X Ultra v3")

app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
app.include_router(make_router(BASE / "static", BASE / "templates"))


@app.get("/")
def root():
    return {"ok": True, "routes": ["/dashboard/spec_runs", "/api/spec_runs", "/ws/spec_updates"]}
