# Aurora-X Instrumentation (SPEC-3)
# Structured logging and request timing middleware
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("aurora")


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs request path, status, duration, and request ID.
    Emits structured JSON-like logs for observability.
    """

    async def dispatch(self, request: Request, call_next):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Record start time
        start = time.perf_counter()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = int((time.perf_counter() - start) * 1000)

        # Log structured information
        logger.info(
            {
                "rid": request_id,
                "path": request.url.path,
                "method": request.method,
                "status": response.status_code,
                "duration_ms": duration_ms,
            }
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
