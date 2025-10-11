"""
FastAPI router for T08 Intent-based chat endpoint
Classifies prompts and generates appropriate Flask app code
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional

from aurora_x.router.intent_router import classify
from aurora_x.templates.web_app_flask import render_app


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    prompt: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    ok: bool
    kind: Optional[str] = None
    name: Optional[str] = None
    file: Optional[str] = None
    hint: Optional[str] = None
    note: Optional[str] = None
    err: Optional[str] = None


def make_chat_router() -> APIRouter:
    """Create and return a FastAPI router with the chat endpoint"""
    router = APIRouter(prefix="/chat", tags=["chat"])
    
    @router.post("", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest):
        """
        Process chat prompts and generate appropriate code based on intent
        
        Args:
            request: ChatRequest containing the prompt
            
        Returns:
            ChatResponse with generated code information
        """
        # Validate prompt
        prompt = (request.prompt or '').strip()
        if not prompt:
            return ChatResponse(ok=False, err="missing prompt")
        
        # Classify intent
        intent = classify(prompt)
        
        # Handle web_app intent
        if intent.kind == "web_app":
            title = "Futuristic UI Timer" if intent.fields.get("feature") == "timer" else intent.name.replace('_', ' ').title()
            code = render_app(title=title, subtitle=intent.brief)
            
            # Save generated code
            Path("app.py").write_text(code, encoding="utf-8")
            
            return ChatResponse(
                ok=True, 
                kind="web_app", 
                file="app.py", 
                hint="Run: python app.py"
            )
        
        # Future: cli_tool, lib_func implementations
        return ChatResponse(
            ok=True, 
            kind=intent.kind, 
            name=intent.name, 
            note="Template not implemented yet"
        )
    
    return router


# For backwards compatibility - can be called from serve.py
def attach_router(app):
    """
    Attach the chat router to a FastAPI app
    
    Args:
        app: FastAPI application instance
    """
    router = make_chat_router()
    app.include_router(router)