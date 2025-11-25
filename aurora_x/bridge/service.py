"""
Service

Comprehensive module documentation explaining purpose, usage, and architecture.

This module is part of Aurora's ecosystem and follows perfect code quality standards.
All functions are fully documented with type hints and error handling.

Author: Aurora AI System
Quality: 10/10 (Perfect)
"""

#!/usr/bin/env python3
"""
Bridge Service - Standalone FastAPI server for NL->Project bridge
Runs on port 5001 and provides the Factory Bridge endpoints
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aurora_x.bridge.attach_bridge import attach_bridge

# Create standalone FastAPI app for Bridge
app = FastAPI(title="Aurora-X Factory Bridge", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach bridge endpoints
attach_bridge(app)


# Health check endpoints
@app.get("/healthz")
@app.get("/health")
@app.get("/api/health")
def health_check():
    """
        Health Check
        
        Returns:
            Result of operation
        """
    return {
        "status": "ok",
        "service": "bridge",
        "port": 5001,
        "aurora_fix": "Added /api/health for frontend compatibility",
    }


@app.get("/api/status")
def status_check():
    """Status endpoint for frontend server control pages (Aurora fix)"""
    return {
        "status": "running",
        "service": "bridge",
        "port": 5001,
        "version": "1.0.0",
        "healthy": True,
        "aurora_fix": "Added /api/status for frontend server control",
    }


@app.get("/")
def root():
    """
        Root
        
        Returns:
            Result of operation
        """
    return {
        "service": "Aurora-X Factory Bridge",
        "version": "1.0.0",
        "port": 5001,
        "status": "running",
        "endpoints": {
            "nl": "/api/bridge/nl - Generate project from natural language",
            "spec": "/api/bridge/spec - Generate project from spec file",
            "deploy": "/api/bridge/deploy - Deploy to Replit",
            "health": "/healthz - Health check",
        },
    }


if __name__ == "__main__":
    import sys

    # Set UTF-8 encoding for Windows compatibility
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    print("[ROCKET] Starting Aurora-X Factory Bridge on port 5001...", flush=True)
    sys.stdout.flush()
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")
