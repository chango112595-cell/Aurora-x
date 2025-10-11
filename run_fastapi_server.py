#!/usr/bin/env python3
"""Run the FastAPI server with the /chat endpoint"""

import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

if __name__ == "__main__":
    print("Starting FastAPI server with T08 Intent Router...")
    print("=" * 60)
    print("Server will run on: http://127.0.0.1:8000")
    print("Available endpoints:")
    print("  - POST /chat - Intent-based chat endpoint")
    print("  - POST /api/chat - English mode chat endpoint") 
    print("  - GET /api/english/status - English mode status")
    print("  - GET / - Root endpoint with routes list")
    print("=" * 60)
    
    # Run the FastAPI server
    uvicorn.run(
        "aurora_x.serve:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )