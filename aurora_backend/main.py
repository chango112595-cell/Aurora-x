#!/usr/bin/env python3
"""
Aurora AI Backend - FastAPI Service
Handles all AI intelligence, NLP, and chat processing
"""

import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent directory to path to import aurora modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from aurora.core.aurora_conversation_intelligence import AuroraCoreIntelligence

    AURORA_AVAILABLE = True
except ImportError:
    AURORA_AVAILABLE = False
    logging.error("Aurora core not available; backend will respond with 503 until restored.")

app = FastAPI(title="Aurora AI Core", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("uvicorn.error")

# Initialize Aurora if available
aurora_core = None
if AURORA_AVAILABLE:
    try:
        aurora_core = AuroraCoreIntelligence()
        logger.info("Aurora Core Intelligence initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Aurora Core: {e}")


class ChatMessage(BaseModel):
    text: str
    session_id: str = "default"
    context: dict = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        self.active_connections[session_id] = ws
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")

    async def send_message(self, session_id: str, message: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)


manager = ConnectionManager()


@app.get("/healthz")
async def health():
    return {
        "status": "ok",
        "service": "aurora-ai-backend",
        "aurora_core": "available" if AURORA_AVAILABLE and aurora_core else "unavailable",
    }


@app.get("/api/info")
async def info():
    return {
        "service": "aurora-ai-backend",
        "version": "1.0.0",
        "description": "Aurora AI Core Intelligence Service",
        "aurora_modules": AURORA_AVAILABLE,
    }


@app.post("/api/chat")
async def chat_endpoint(msg: ChatMessage):
    """Process chat message through Aurora intelligence"""
    try:
        if not aurora_core:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Aurora core not initialized",
            )
        # Use Aurora's conversation intelligence
        context = aurora_core.get_conversation_context(msg.session_id)
        result = aurora_core.analyze_natural_language(msg.text, context)
        return {
            "response": result.get("response", "Processing..."),
            "intent": result.get("intent"),
            "entities": result.get("entities", {}),
            "session_id": msg.session_id,
        }
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        return {
            "response": "I encountered an error processing your message.",
            "error": str(e),
            "session_id": msg.session_id,
        }


@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(ws: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    if not aurora_core:
        await ws.accept()
        await ws.send_text("Aurora core not initialized")
        await ws.close(code=1011)
        return
    await manager.connect(session_id, ws)
    try:
        while True:
            data = await ws.receive_text()

            # Process through Aurora if available
            if aurora_core:
                context = aurora_core.get_conversation_context(session_id)
                result = aurora_core.analyze_natural_language(data, context)
                response = result.get("response", "Processing...")
            else:
                response = f"Echo: {data}"

            await manager.send_message(session_id, response)

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
