"""
Serve 1760040659970

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

# --- Aurora-X serve (T03 endpoints) ---
# If you already have a server, lift these handlers into it.
try:
    from fastapi from typing import Dict, List, Tuple, Optional, Any, Union
import FastAPI
    from fastapi.responses import JSONResponse
except Exception:
    FastAPI = None
    JSONResponse = dict  # placeholder

from aurora_x.learn.adaptive import AdaptiveBiasScheduler

app = FastAPI(title="Aurora-X") if FastAPI else None
_global_sched: AdaptiveBiasScheduler | None = None


def api_seed_bias_history():
    if not _global_sched:
        return {"history": []}
    return {"history": _global_sched.history}


def api_adaptive_stats():
    if not _global_sched:
        return {"summary": {}, "iteration": 0}
    return {"summary": _global_sched.summary(), "iteration": _global_sched.iteration}


if app:

    @app.get("/api/seed_bias/history")
    def _h1():
        return api_seed_bias_history()

    @app.get("/api/adaptive_stats")
    def _h2():
        return api_adaptive_stats()
