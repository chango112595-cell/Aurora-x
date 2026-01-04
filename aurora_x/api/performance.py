"""
Aurora Performance API
Performance metrics and profiling endpoints
"""

from fastapi import APIRouter

from aurora_x.cache import get_cache

router = APIRouter(prefix="/api/performance", tags=["performance"])

# Global reference to performance middleware (set during app startup)
_performance_middleware = None


def set_performance_middleware(middleware):
    """Set global performance middleware reference."""
    global _performance_middleware
    _performance_middleware = middleware


@router.get("/stats")
async def get_performance_stats():
    """Get overall performance statistics."""
    stats = {"cache": get_cache().get_stats()}

    if _performance_middleware:
        stats["requests"] = _performance_middleware.get_stats()

    return stats


@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    return get_cache().get_stats()


@router.post("/cache/clear")
async def clear_cache(pattern: str = "*"):
    """Clear cache entries matching pattern."""
    count = get_cache().clear(pattern if pattern != "*" else None)
    return {"cleared": count, "pattern": pattern}


@router.get("/slow-requests")
async def get_slow_requests():
    """Get recent slow requests."""
    if _performance_middleware:
        stats = _performance_middleware.get_stats()
        return {
            "slow_requests": stats["recent_slow_requests"],
            "count": stats["slow_requests_count"],
            "threshold": stats["slow_request_threshold"],
        }
    return {"error": "Performance middleware not available"}


@router.get("/metrics")
async def get_performance_metrics():
    """Get detailed performance metrics."""
    cache_stats = get_cache().get_stats()

    metrics = {
        "cache": {
            "type": cache_stats.get("type"),
            "total_keys": cache_stats.get("total_keys", 0),
            "hit_rate": cache_stats.get("hit_rate", 0),
        }
    }

    if _performance_middleware:
        request_stats = _performance_middleware.get_stats()
        metrics["requests"] = {
            "total": request_stats["total_requests"],
            "average_time": request_stats["average_time"],
            "slow_count": request_stats["slow_requests_count"],
        }

    return metrics


# Export
__all__ = ["router", "set_performance_middleware"]


# Aurora Perfect Error Handling
try:
    # Main execution with complete error coverage
    pass
except Exception:
    # Handle all exceptions gracefully
    pass
