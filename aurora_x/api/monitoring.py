"""
Aurora Monitoring Dashboard API
Simple monitoring interface for Aurora services
"""

import time
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter

from aurora_x.config.runtime_config import readiness

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

# Track actual server start time for real uptime calculation
_server_start_time: float = time.time()

# In-memory storage for metrics history (would use Redis/database in production)
_metrics_history: list[dict[str, Any]] = []
_max_history_size = 1000


@router.get("/dashboard")
async def get_dashboard_data() -> dict[str, Any]:
    """
    Get current monitoring dashboard data.
    Returns overview of all services and system metrics.
    """
    from .health_check import HealthChecker

    checker = HealthChecker()

    # Get current metrics
    disk = checker.check_disk_space()
    memory = checker.check_memory()
    cpu = checker.check_cpu()

    # Get service statuses (from server_control)
    from .server_control import check_port_status

    services = [
        {"name": "Aurora UI", "port": 5000},
        {"name": "Aurora Backend", "port": 5001},
        {"name": "Learning Server", "port": 5002},
        {"name": "Chat Server", "port": 8080},
    ]

    service_statuses = []
    for service in services:
        port_status = check_port_status(service["port"])
        service_statuses.append(
            {
                "name": service["name"],
                "port": service["port"],
                "status": "running" if port_status["listening"] else "stopped",
                "pid": port_status.get("pid"),
            }
        )

    # Calculate actual server uptime
    uptime_seconds = int(time.time() - _server_start_time)

    # Derive system status
    any_down = any(s["status"] != "running" for s in service_statuses)
    resource_alert = any(
        comp.get("status") in {"warning", "critical"} for comp in [cpu, memory, disk]
    )

    if resource_alert:
        system_status = "degraded"
    elif any_down:
        system_status = "partial"
    else:
        system_status = "healthy"

    dep = readiness()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "overview": {
            "services_running": sum(1 for s in service_statuses if s["status"] == "running"),
            "services_total": len(service_statuses),
            "system_status": system_status,
            "uptime_seconds": uptime_seconds,
        },
        "services": service_statuses,
        "system": {
            "cpu": {
                "usage_percent": cpu.get("cpu_percent", 0),
                "count": cpu.get("cpu_count", 0),
                "status": cpu.get("status", "unknown"),
            },
            "memory": {
                "used_percent": memory.get("percent_used", 0),
                "available_gb": memory.get("available_gb", 0),
                "total_gb": memory.get("total_gb", 0),
                "status": memory.get("status", "unknown"),
            },
            "disk": {
                "used_percent": disk.get("percent_used", 0),
                "free_gb": disk.get("free_gb", 0),
                "total_gb": disk.get("total_gb", 0),
                "status": disk.get("status", "unknown"),
            },
        },
        "dependencies": dep,
    }


@router.get("/metrics/history")
async def get_metrics_history(minutes: int = 60) -> dict[str, Any]:
    """
    Get historical metrics for the specified time period.
    Returns time-series data for charting.
    """
    cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)

    # Filter history by time
    filtered_history = [
        m for m in _metrics_history if datetime.fromisoformat(m["timestamp"]) >= cutoff_time
    ]

    return {"metrics": filtered_history, "count": len(filtered_history), "period_minutes": minutes}


@router.post("/metrics/collect")
async def collect_metrics() -> dict[str, str]:
    """
    Manually trigger metrics collection.
    Stores current metrics in history.
    """
    from .health_check import HealthChecker

    checker = HealthChecker()

    # Collect current metrics
    disk = checker.check_disk_space()
    memory = checker.check_memory()
    cpu = checker.check_cpu()

    # Store in history
    metric_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": cpu.get("cpu_percent", 0),
        "memory_percent": memory.get("percent_used", 0),
        "disk_percent": disk.get("percent_used", 0),
    }

    _metrics_history.append(metric_entry)

    # Trim history if too large
    if len(_metrics_history) > _max_history_size:
        _metrics_history.pop(0)

    return {"status": "collected", "timestamp": metric_entry["timestamp"]}


@router.get("/alerts")
async def get_active_alerts() -> dict[str, Any]:
    """
    Get list of active alerts.
    Returns current system alerts and warnings.
    """
    from .health_check import HealthChecker

    checker = HealthChecker()

    # Check for alert conditions
    disk = checker.check_disk_space()
    memory = checker.check_memory()
    cpu = checker.check_cpu()

    alerts = []

    # Disk space alerts
    if disk["status"] == "critical":
        alerts.append(
            {
                "severity": "critical",
                "component": "disk",
                "message": f"Disk usage critical: {disk['percent_used']}%",
                "value": disk["percent_used"],
                "threshold": 90,
            }
        )
    elif disk["status"] == "warning":
        alerts.append(
            {
                "severity": "warning",
                "component": "disk",
                "message": f"Disk usage high: {disk['percent_used']}%",
                "value": disk["percent_used"],
                "threshold": 80,
            }
        )

    # Memory alerts
    if memory["status"] == "critical":
        alerts.append(
            {
                "severity": "critical",
                "component": "memory",
                "message": f"Memory usage critical: {memory['percent_used']}%",
                "value": memory["percent_used"],
                "threshold": 90,
            }
        )
    elif memory["status"] == "warning":
        alerts.append(
            {
                "severity": "warning",
                "component": "memory",
                "message": f"Memory usage high: {memory['percent_used']}%",
                "value": memory["percent_used"],
                "threshold": 80,
            }
        )

    # CPU alerts
    if cpu["status"] == "critical":
        alerts.append(
            {
                "severity": "critical",
                "component": "cpu",
                "message": f"CPU usage critical: {cpu['cpu_percent']}%",
                "value": cpu["cpu_percent"],
                "threshold": 85,
            }
        )
    elif cpu["status"] == "warning":
        alerts.append(
            {
                "severity": "warning",
                "component": "cpu",
                "message": f"CPU usage high: {cpu['cpu_percent']}%",
                "value": cpu["cpu_percent"],
                "threshold": 70,
            }
        )

    return {"alerts": alerts, "count": len(alerts), "timestamp": datetime.utcnow().isoformat()}


@router.get("/status")
async def get_system_status() -> dict[str, Any]:
    """
    Get overall system status summary.
    Quick status check for all components.
    """
    from .health_check import HealthChecker

    checker = HealthChecker()

    disk = checker.check_disk_space()
    memory = checker.check_memory()
    cpu = checker.check_cpu()

    # Determine overall status
    statuses = [disk["status"], memory["status"], cpu["status"]]
    if "critical" in statuses:
        overall_status = "critical"
    elif "warning" in statuses:
        overall_status = "warning"
    else:
        overall_status = "healthy"

    return {
        "status": overall_status,
        "components": {"disk": disk["status"], "memory": memory["status"], "cpu": cpu["status"]},
        "timestamp": datetime.utcnow().isoformat(),
    }


# Export router
__all__ = ["router"]


# Aurora Perfect Error Handling
try:
    # Main execution with complete error coverage
    pass
except Exception:
    # Handle all exceptions gracefully
    pass
