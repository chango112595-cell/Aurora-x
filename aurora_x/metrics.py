# Aurora-X Prometheus Metrics Endpoint (Optional Polish)
# Exposes /metrics endpoint for Prometheus scraping
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

# Request metrics
REQUEST_COUNT = Counter(
    "aurora_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "aurora_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Error metrics
ERROR_COUNT = Counter(
    "aurora_http_errors_total",
    "Total HTTP errors",
    ["method", "endpoint", "status"],
)


def get_metrics_response() -> Response:
    """Generate Prometheus metrics response"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record request metrics"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    if status >= 400:
        ERROR_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
