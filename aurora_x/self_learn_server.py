#!/usr/bin/env python3
"""
Aurora-X Self-Learning Server
Dedicated server for continuous self-learning with independent monitoring.
"""

import json
import time
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from aurora_x.self_learn import SelfLearningDaemon

app = FastAPI(title="Aurora-X Self-Learning Server")

# Dedicated directories for self-learning
SELF_LEARN_SPEC_DIR = Path("specs_learning")
SELF_LEARN_OUTPUT_DIR = Path("runs_learning")

# Global daemon instance
daemon = None
daemon_stats = {
    "started_at": None,
    "total_runs": 0,
    "successful_runs": 0,
    "failed_runs": 0,
    "last_run_time": None,
    "status": "stopped",
}


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "Aurora-X Self-Learning Server",
        "status": daemon_stats["status"],
        "routes": ["/health", "/stats", "/start", "/stop", "/recent-runs"],
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "ok": True,
        "service": "self-learning",
        "status": daemon_stats["status"],
        "port": 5002,
        "timestamp": time.time(),
    }


@app.get("/api/health")
def api_health():
    """API health check endpoint for frontend compatibility (Aurora fix)"""
    return {
        "ok": True,
        "service": "self-learning",
        "status": daemon_stats["status"],
        "port": 5002,
        "timestamp": time.time(),
        "aurora_fix": "Added /api/health route for frontend compatibility",
    }


@app.get("/stats")
def get_stats():
    """Get self-learning statistics"""
    return JSONResponse(
        content={
            "ok": True,
            "stats": daemon_stats,
            "spec_dir": str(SELF_LEARN_SPEC_DIR),
            "output_dir": str(SELF_LEARN_OUTPUT_DIR),
        }
    )


@app.post("/start")
def start_learning(sleep_seconds: int = 300, max_iters: int = 50, beam: int = 20):
    """Start self-learning daemon (if not already running)"""
    global daemon, daemon_stats

    if daemon_stats["status"] == "running":
        return JSONResponse(content={"ok": False, "error": "Self-learning daemon already running"}, status_code=400)

    # Create directories if they don't exist
    SELF_LEARN_SPEC_DIR.mkdir(exist_ok=True)
    SELF_LEARN_OUTPUT_DIR.mkdir(exist_ok=True)

    # Initialize daemon
    daemon = SelfLearningDaemon(
        spec_dir=SELF_LEARN_SPEC_DIR,
        outdir=SELF_LEARN_OUTPUT_DIR,
        sleep_seconds=sleep_seconds,
        max_iters=max_iters,
        beam=beam,
    )

    daemon_stats["status"] = "running"
    daemon_stats["started_at"] = datetime.now().isoformat()

    # Note: In production, you'd run this in a background thread or process
    # For now, we'll just mark it as ready

    return JSONResponse(
        content={
            "ok": True,
            "message": "Self-learning daemon configured (use background process to actually run)",
            "config": {"sleep_seconds": sleep_seconds, "max_iters": max_iters, "beam": beam},
        }
    )


@app.post("/stop")
def stop_learning():
    """Stop self-learning daemon"""
    global daemon_stats

    if daemon_stats["status"] != "running":
        return JSONResponse(content={"ok": False, "error": "Self-learning daemon not running"}, status_code=400)

    daemon_stats["status"] = "stopped"

    return JSONResponse(content={"ok": True, "message": "Self-learning daemon stopped"})


@app.get("/recent-runs")
def get_recent_runs(limit: int = 10):
    """Get recent self-learning runs"""
    runs = []

    if SELF_LEARN_OUTPUT_DIR.exists():
        run_dirs = sorted(SELF_LEARN_OUTPUT_DIR.glob("run-*"), reverse=True)

        for run_dir in run_dirs[:limit]:
            meta_file = run_dir / "run_meta.json"
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text())
                    runs.append(
                        {
                            "run_id": run_dir.name,
                            "started": meta.get("start_ts"),
                            "duration": meta.get("duration_seconds"),
                            "path": str(run_dir),
                        }
                    )
                except Exception:
                    pass

    return JSONResponse(content={"ok": True, "runs": runs, "total_found": len(runs)})


def main():
    """Entry point for self-learning server"""
    import os

    port = int(os.getenv("SELF_LEARN_PORT", "5002"))
    print(f"[Aurora-X Self-Learning] Starting server on 0.0.0.0:{port}")
    print(f"  Spec directory: {SELF_LEARN_SPEC_DIR}")
    print(f"  Output directory: {SELF_LEARN_OUTPUT_DIR}")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
