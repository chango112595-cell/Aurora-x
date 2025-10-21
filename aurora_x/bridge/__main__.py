#!/usr/bin/env python3
"""
Bridge Service Main Entry Point
Run with: python -m aurora_x.bridge.service
"""

import argparse

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aurora_x.bridge.attach_bridge import attach_bridge


def main():
    parser = argparse.ArgumentParser(description="Aurora-X Factory Bridge Service")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5001, help="Port to bind to")
    args = parser.parse_args()

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
        return {"status": "ok", "service": "bridge", "port": args.port}

    @app.get("/")
    def root():
        return {
            "service": "Aurora-X Factory Bridge",
            "endpoints": [
                "/api/bridge/nl - Generate project from natural language",
                "/api/bridge/spec - Generate project from spec file",
                "/api/bridge/deploy - Deploy to Replit",
                "/healthz - Health check"
            ]
        }

    print(f"🚀 Starting Aurora-X Factory Bridge on {args.host}:{args.port}...")
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
