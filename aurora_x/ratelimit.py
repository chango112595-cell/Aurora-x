# Aurora-X Rate Limiting (SPEC-4)
# Simple in-memory rate limiting middleware
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Default rate limit: 120 requests per 60 seconds per IP
WINDOW_SECONDS = 60
MAX_REQUESTS = 120


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    Tracks requests per client IP using a sliding window.
    """

    def __init__(self, app, window_seconds: int = WINDOW_SECONDS, max_requests: int = MAX_REQUESTS):
        super().__init__(app)
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        # Store request timestamps per client IP
        self.store: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Clean old entries outside the window
        now = time.time()
        dq = self.store[client_ip]

        # Remove timestamps outside the window
        while dq and now - dq[0] > self.window_seconds:
            dq.popleft()

        # Check if limit exceeded
        if len(dq) >= self.max_requests:
            return JSONResponse(
                {"detail": "Rate limit exceeded", "retry_after": self.window_seconds},
                status_code=429,
            )

        # Add current request timestamp
        dq.append(now)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = max(0, self.max_requests - len(dq))
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + self.window_seconds))

        return response
