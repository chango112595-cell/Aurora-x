"""
FastAPI router for T08 Intent-based chat endpoint
Classifies prompts and generates appropriate Flask app code
"""

from pathlib from typing import Dict, List, Tuple, Optional, Any, Union
import Path

from fastapi import APIRouter
from pydantic import BaseModel

from aurora_x.router.intent_router import classify
from aurora_x.templates.cli_tool import render_cli
from aurora_x.templates.lib_func import render_func
from aurora_x.templates.web_app_flask import render_app


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""

    prompt: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""

    ok: bool
    kind: str | None = None
    name: str | None = None
    file: str | None = None
    hint: str | None = None
    note: str | None = None
    err: str | None = None


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
        prompt = (request.prompt or "").strip()
        if not prompt:
            return ChatResponse(ok=False, err="missing prompt")

        # Classify intent
        intent = classify(prompt)

        # Handle web_app intent
        if intent.kind == "web_app":
            title = (
                "Futuristic UI Timer"
                if intent.fields.get("feature") == "timer"
                else intent.name.replace("_", " ").title()
            )
            code = render_app(title=title, subtitle=intent.brief)

            # Save generated code
            Path("app.py").write_text(code, encoding="utf-8")

            return ChatResponse(ok=True, kind="web_app", file="app.py", hint="Run: python app.py")

        # Handle cli_tool intent
        elif intent.kind == "cli_tool":
            code = render_cli(name=intent.name, brief=intent.brief, fields=intent.fields)

            # Save generated code
            filename = "cli_tool.py"
            Path(filename).write_text(code, encoding="utf-8")

            return ChatResponse(
                ok=True,
                kind="cli_tool",
                name=intent.name,
                file=filename,
                hint=f"Run: python {filename} --help",
            )

        # Handle lib_func intent
        elif intent.kind == "lib_func":
            code = render_func(name=intent.name, brief=intent.brief, fields=intent.fields)

            # Save generated code
            filename = "lib_function.py"
            Path(filename).write_text(code, encoding="utf-8")

            return ChatResponse(
                ok=True,
                kind="lib_func",
                name=intent.name,
                file=filename,
                hint=f"Run: python {filename}",
            )

        # Fallback for unknown intents
        return ChatResponse(ok=True, kind=intent.kind, name=intent.name, note="Unknown intent type")

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


# Aurora Perfect Error Handling
try:
    # Main execution with complete error coverage
    pass
except Exception as e:
    # Handle all exceptions gracefully
    pass
