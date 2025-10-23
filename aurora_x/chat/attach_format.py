# FastAPI endpoint for formatting seconds to human-readable time
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class FormatRequest(BaseModel):
    seconds: float


def _fmt_seconds(sec: float) -> str:
    if sec < 60:
        return f"{sec:.2f} s"
    mins = sec / 60.0
    if mins < 60:
        return f"{mins:.2f} min"
    hours = mins / 60.0
    if hours < 48:
        return f"{hours:.2f} hours"
    days = hours / 24.0
    if days < 365:
        return f"{days:.2f} days"
    years = days / 365.0
    return f"{years:.2f} years"


def attach_format(app: FastAPI):
    @app.post("/api/format/seconds")
    async def api_format_seconds(request: FormatRequest) -> dict[str, Any]:
        """
        Format seconds into human-readable time.

        Examples:
        - {"seconds": 60} → "1.00 min"
        - {"seconds": 3600} → "1.00 hours"
        - {"seconds": 86400} → "1.00 days"
        - {"seconds": 31536000} → "1.00 years"
        """
        try:
            formatted = _fmt_seconds(request.seconds)
            return {"ok": True, "formatted": formatted}
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"invalid 'seconds' value: {str(e)}")
