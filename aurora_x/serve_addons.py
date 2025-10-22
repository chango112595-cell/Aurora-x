"""
Aurora-X English Mode API Addons
Provides chat and approval endpoints for natural language synthesis
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aurora_x.spec.parser_v2 import _snake, english_to_spec


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    prompt: str
    auto_synthesize: bool = False  # Whether to immediately trigger synthesis

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    ok: bool
    spec: str  # Path to generated spec
    function_name: str | None = None
    message: str | None = None
    synthesis_started: bool = False

class ApprovalRequest(BaseModel):
    """Request model for approval endpoint"""
    token: str
    approved: bool

def attach(app: FastAPI) -> None:
    """Attach English mode routes to the FastAPI app"""

    # Ensure requests directory exists
    requests_dir = Path("specs/requests")
    requests_dir.mkdir(parents=True, exist_ok=True)

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest):
        """
        Accept plain English prompt and generate V3 spec

        Args:
            request: ChatRequest with prompt and optional auto_synthesize flag

        Returns:
            ChatResponse with spec path and status
        """
        try:
            # Validate prompt
            if not request.prompt or not request.prompt.strip():
                raise HTTPException(status_code=400, detail="Empty prompt provided")

            # Generate spec content using English-to-spec conversion
            spec_content = english_to_spec(request.prompt)

            # Save spec to file
            filename = f"{_snake(request.prompt)}.md"
            spec_path = requests_dir / filename

            with open(spec_path, 'w') as f:
                f.write(spec_content)

            # Extract function name from spec
            import re
            func_match = re.search(r'def\s+(\w+)\s*\(', spec_content)
            function_name = func_match.group(1) if func_match else "unknown"

            response_data = {
                "ok": True,
                "spec": str(spec_path),
                "function_name": function_name,
                "message": f"Spec generated successfully for: {request.prompt[:100]}",
                "synthesis_started": False
            }

            # Optionally trigger synthesis
            if request.auto_synthesize:
                try:
                    # Use the V3 spec compiler
                    result = subprocess.run(
                        ["python", "tools/spec_compile_v3.py", str(spec_path)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if result.returncode == 0:
                        response_data["synthesis_started"] = True
                        response_data["message"] += " | Synthesis completed successfully"
                    else:
                        response_data["message"] += f" | Synthesis failed: {result.stderr[:200]}"

                except subprocess.TimeoutExpired:
                    response_data["message"] += " | Synthesis timed out"
                except Exception as e:
                    response_data["message"] += f" | Synthesis error: {str(e)[:200]}"

            return ChatResponse(**response_data)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process prompt: {str(e)}"
            )

    @app.get("/api/approve")
    async def approve_endpoint(token: str | None = None):
        """
        Optional approval mechanism for synthesis runs

        This endpoint can be extended to implement approval workflows
        where synthesis runs need manual approval before execution.

        Args:
            token: Optional approval token

        Returns:
            Approval status and pending runs
        """
        # For now, return a placeholder response
        # This can be extended with actual approval logic
        pending_runs = []

        # Check for any pending specs in requests directory
        if requests_dir.exists():
            for spec_file in requests_dir.glob("*.md"):
                # Check if this spec has been synthesized
                # (You could track this in a database or file)
                pending_runs.append({
                    "spec": str(spec_file),
                    "created": datetime.fromtimestamp(spec_file.stat().st_mtime).isoformat(),
                    "token": hashlib.sha256(str(spec_file).encode()).hexdigest()[:8]
                    "token": hashlib.md5(str(spec_file).encode(), usedforsecurity=False).hexdigest()[:8]
                })

        return {
            "ok": True,
            "pending_runs": pending_runs[:10],  # Limit to last 10
            "message": f"Found {len(pending_runs)} pending specs"
        }

    @app.post("/api/approve")
    async def approve_synthesis(request: ApprovalRequest):
        """
        Approve or reject a pending synthesis run

        Args:
            request: ApprovalRequest with token and approval status

        Returns:
            Result of approval action
        """
        # For now, return a placeholder response
        # This can be extended to actually trigger or cancel synthesis
        return {
            "ok": True,
            "token": request.token,
            "approved": request.approved,
            "message": f"Synthesis {'approved' if request.approved else 'rejected'} for token {request.token}"
        }

    @app.get("/api/english/status")
    async def english_mode_status():
        """Get status of English mode features"""
        return {
            "ok": True,
            "english_mode_enabled": True,
            "endpoints": [
                "/api/chat - Generate spec from English prompt",
                "/api/approve - Manage synthesis approvals",
                "/api/english/status - This status endpoint"
            ],
            "specs_directory": str(requests_dir),
            "fallback_enabled": True,
            "message": "English mode is active and ready to accept plain language requests"
        }

    # Log that addons have been attached
    print("✅ Aurora-X English Mode API addons attached")
    print("   - POST /api/chat - Accept English prompts")
    print("   - GET/POST /api/approve - Approval mechanism")
    print("   - GET /api/english/status - English mode status")
