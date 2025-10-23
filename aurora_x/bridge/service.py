#!/usr/bin/env python3
"""
Bridge Service - Standalone FastAPI server for NL→Project bridge
Runs on port 5001 and provides the Factory Bridge endpoints
"""

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


# Health check endpoint
@app.get("/healthz")
def health_check():
    return {"status": "ok", "service": "bridge", "port": 5001}


@app.get("/")
def root():
    return {
        "service": "Aurora-X Factory Bridge",
        "endpoints": [
            "/api/bridge/nl - Generate project from natural language",
            "/api/bridge/spec - Generate project from spec file",
            "/api/bridge/deploy - Deploy to Replit",
            "/healthz - Health check",
        ],
    }


if __name__ == "__main__":
    import sys
    print("🚀 Starting Aurora-X Factory Bridge on port 5001...", flush=True)
    sys.stdout.flush()
    uvicorn.run(app, host="0.0.0.0", port=5001)
