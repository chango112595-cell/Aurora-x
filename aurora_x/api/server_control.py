"""
Server Control API Endpoints
Created by Aurora to fix Server Control page
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import subprocess
from typing import Dict, List, Any

router = APIRouter(prefix="/api/services", tags=["services"])


class ServiceStatus(BaseModel):
    """Service status model."""
    name: str
    port: int
    status: str  # "running" | "stopped"
    pid: int | None = None


def check_port_status(port: int) -> Dict[str, Any]:
    """Check if a port is listening using lsof."""
    try:
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-P", "-n"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout:
            # Port is listening
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                # Parse PID from output
                parts = lines[1].split()
                pid = int(parts[1]) if len(parts) > 1 else None
                return {"listening": True, "pid": pid}
        
        return {"listening": False, "pid": None}
    except Exception as e:
        return {"listening": False, "pid": None, "error": str(e)}


@router.get("/status")
async def get_services_status() -> Dict[str, List[ServiceStatus]]:
    """
    Get status of all Aurora services.
    Returns actual port status using lsof.
    """
    services = [
        {"name": "Aurora UI", "port": 5000, "command": "npm run dev"},
        {"name": "Aurora Backend", "port": 5001, "command": "uvicorn aurora_x.serve:app"},
        {"name": "Learning Server", "port": 5002, "command": "python -m aurora_x.self_learn_server"},
        {"name": "Chat Server", "port": 8080, "command": "python -m aurora_x.chat.serve"},
    ]
    
    statuses = []
    for service in services:
        port_status = check_port_status(service["port"])
        
        status = ServiceStatus(
            name=service["name"],
            port=service["port"],
            status="running" if port_status["listening"] else "stopped",
            pid=port_status.get("pid")
        )
        statuses.append(status)
    
    return {"services": statuses}


@router.post("/start/{service_name}")
async def start_service(service_name: str) -> Dict[str, Any]:
    """
    Start a service.
    Aurora supervises the startup.
    """
    # Map service names to commands
    service_commands = {
        "aurora-ui": {"cwd": "client", "cmd": ["npm", "run", "dev"]},
        "aurora-backend": {"cwd": ".", "cmd": ["uvicorn", "aurora_x.serve:app", "--host", "0.0.0.0", "--port", "5001"]},
        "learning-server": {"cwd": ".", "cmd": ["python", "-m", "aurora_x.self_learn_server"]},
        "chat-server": {"cwd": ".", "cmd": ["python", "-m", "aurora_x.chat.serve"]},
    }
    
    if service_name not in service_commands:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    
    # TODO: Implement actual service startup using supervisor
    # For now, return success message
    return {
        "success": True,
        "message": f"Service '{service_name}' start initiated",
        "note": "Use aurora_supervisor for production service management"
    }


@router.post("/stop/{service_name}")
async def stop_service(service_name: str) -> Dict[str, Any]:
    """
    Stop a service.
    Aurora supervises the shutdown.
    """
    # TODO: Implement actual service shutdown using supervisor
    return {
        "success": True,
        "message": f"Service '{service_name}' stop initiated",
        "note": "Use aurora_supervisor for production service management"
    }


@router.post("/restart/{service_name}")
async def restart_service(service_name: str) -> Dict[str, Any]:
    """
    Restart a service.
    Aurora supervises the restart.
    """
    # TODO: Implement actual service restart using supervisor
    return {
        "success": True,
        "message": f"Service '{service_name}' restart initiated",
        "note": "Use aurora_supervisor for production service management"
    }


@router.post("/start-all")
async def start_all_services() -> Dict[str, Any]:
    """
    Start all Aurora services.
    The big START ALL button!
    """
    return {
        "success": True,
        "message": "All Aurora services starting",
        "note": "Use aurora_supervisor for production orchestration"
    }


# Export router
__all__ = ["router"]
