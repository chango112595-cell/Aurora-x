#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aurora_x.bridge.attach_bridge import attach_bridge

app = FastAPI(title="Aurora-X Bridge API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach all bridge endpoints
attach_bridge(app)


@app.get("/")
def root():
    return {"message": "Aurora-X Bridge API is running", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "bridge-api"}


if __name__ == "__main__":
    import uvicorn

    print("🌉 Starting Aurora Bridge API on port 5001...")
    print("📍 Comparison endpoints available at /api/bridge/comparison/*")

    uvicorn.run(app, host="0.0.0.0", port=5001)
