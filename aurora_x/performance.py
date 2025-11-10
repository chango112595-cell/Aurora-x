"""
Aurora Performance Profiling Middleware
Request timing and performance monitoring
"""

import time
from datetime import datetime
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track request performance metrics.
    Measures response time and logs slow requests.
    """

    def __init__(self, app, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold  # seconds
        self.request_count = 0
        self.total_time = 0.0
        self.slow_requests = []

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Update statistics
        self.request_count += 1
        self.total_time += duration

        # Track slow requests
        if duration > self.slow_request_threshold:
            slow_request = {
                "method": request.method,
                "path": request.url.path,
                "duration": round(duration, 3),
                "timestamp": datetime.utcnow().isoformat(),
            }
            self.slow_requests.append(slow_request)

            # Keep only last 100 slow requests
            if len(self.slow_requests) > 100:
                self.slow_requests.pop(0)

            print(f"⚠️  Slow request detected: {request.method} {request.url.path} ({duration:.3f}s)")

        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        return response

    def get_stats(self) -> dict:
        """Get performance statistics."""
        avg_time = self.total_time / self.request_count if self.request_count > 0 else 0

        return {
            "total_requests": self.request_count,
            "total_time": round(self.total_time, 3),
            "average_time": round(avg_time, 3),
            "slow_requests_count": len(self.slow_requests),
            "slow_request_threshold": self.slow_request_threshold,
            "recent_slow_requests": self.slow_requests[-10:] if self.slow_requests else [],
        }


# Export
__all__ = ["PerformanceMiddleware"]
