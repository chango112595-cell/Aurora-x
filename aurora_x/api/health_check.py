"""
Aurora Health Check System
Comprehensive health monitoring for all services
"""

from datetime import datetime
from typing import Any

import psutil
from fastapi import APIRouter, Response

router = APIRouter(prefix="/api/health", tags=["health"])


class HealthChecker:
    """Health check utilities for Aurora services."""

    @staticmethod
    def check_database() -> dict[str, Any]:
        """Check database connectivity."""
        # TODO: Implement actual database check when PostgreSQL is set up
        return {
            "status": "healthy",
            "message": "Database check not implemented (no DB configured)",
            "latency_ms": 0,
        }

    @staticmethod
    def check_disk_space() -> dict[str, Any]:
        """Check available disk space."""
        try:
            disk = psutil.disk_usage("/")
            percent_used = disk.percent
            status = "healthy" if percent_used < 80 else "warning" if percent_used < 90 else "critical"

            return {
                "status": status,
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent_used": percent_used,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def check_memory() -> dict[str, Any]:
        """Check memory usage."""
        try:
            memory = psutil.virtual_memory()
            percent_used = memory.percent
            status = "healthy" if percent_used < 80 else "warning" if percent_used < 90 else "critical"

            return {
                "status": status,
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percent_used": percent_used,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def check_cpu() -> dict[str, Any]:
        """Check CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            status = "healthy" if cpu_percent < 70 else "warning" if cpu_percent < 85 else "critical"

            return {
                "status": status,
                "cpu_count": cpu_count,
                "cpu_percent": cpu_percent,
                "load_average": psutil.getloadavg() if hasattr(psutil, "getloadavg") else None,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


@router.get("/")
async def health_check() -> dict[str, Any]:
    """
    Basic health check endpoint.
    Returns 200 if service is running.
    """
    return {
        "status": "healthy",
        "service": "Aurora-X",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


@router.get("/detailed")
async def detailed_health_check(response: Response) -> dict[str, Any]:
    """
    Detailed health check with all system metrics.
    Returns comprehensive health information.
    """
    checker = HealthChecker()

    # Collect all health checks
    database = checker.check_database()
    disk = checker.check_disk_space()
    memory = checker.check_memory()
    cpu = checker.check_cpu()

    # Determine overall status
    statuses = [database["status"], disk["status"], memory["status"], cpu["status"]]
    if "critical" in statuses:
        overall_status = "critical"
        response.status_code = 503
    elif "error" in statuses:
        overall_status = "error"
        response.status_code = 503
    elif "warning" in statuses:
        overall_status = "warning"
        response.status_code = 200
    else:
        overall_status = "healthy"
        response.status_code = 200

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Aurora-X",
        "version": "1.0.0",
        "checks": {
            "database": database,
            "disk": disk,
            "memory": memory,
            "cpu": cpu,
        },
    }


@router.get("/liveness")
async def liveness_probe() -> dict[str, str]:
    """
    Kubernetes liveness probe.
    Returns 200 if service is alive.
    """
    return {"status": "alive"}


@router.get("/readiness")
async def readiness_probe(response: Response) -> dict[str, Any]:
    """
    Kubernetes readiness probe.
    Returns 200 if service is ready to accept traffic.
    """
    checker = HealthChecker()

    # Check critical dependencies
    disk = checker.check_disk_space()
    memory = checker.check_memory()

    # Service is ready if disk and memory are not critical
    is_ready = disk["status"] != "critical" and memory["status"] != "critical"

    if not is_ready:
        response.status_code = 503

    return {
        "status": "ready" if is_ready else "not_ready",
        "checks": {"disk": disk["status"], "memory": memory["status"]},
    }


@router.get("/metrics")
async def metrics_endpoint() -> dict[str, Any]:
    """
    Prometheus-compatible metrics endpoint.
    Returns metrics in JSON format.
    """
    checker = HealthChecker()

    disk = checker.check_disk_space()
    memory = checker.check_memory()
    cpu = checker.check_cpu()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "disk_used_percent": disk.get("percent_used", 0),
            "disk_free_gb": disk.get("free_gb", 0),
            "memory_used_percent": memory.get("percent_used", 0),
            "memory_available_gb": memory.get("available_gb", 0),
            "cpu_percent": cpu.get("cpu_percent", 0),
            "cpu_count": cpu.get("cpu_count", 0),
        },
    }


# Export router
__all__ = ["router"]
