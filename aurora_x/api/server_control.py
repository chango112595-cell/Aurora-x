"""
Server Control API Endpoints
Created by Aurora to fix Server Control page
"""

import subprocess
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/services", tags=["services"])


class ServiceStatus(BaseModel):
    """Service status model."""

    name: str
    port: int
    status: str  # "running" | "stopped"
    pid: int | None = None


def check_port_status(port: int) -> dict[str, Any]:
    """Check if a port is listening using lsof."""
    try:
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-P", "-n"], capture_output=True, text=True, timeout=5
        )

        if result.returncode == 0 and result.stdout:
            # Port is listening
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                # Parse PID from output
                parts = lines[1].split()
                pid = int(parts[1]) if len(parts) > 1 else None
                return {"listening": True, "pid": pid}

        return {"listening": False, "pid": None}
    except Exception as e:
        return {"listening": False, "pid": None, "error": str(e)}


@router.get("/status")
async def get_services_status() -> dict[str, list[ServiceStatus]]:
    """
    Get status of all Aurora services.
    Returns actual port status using lsof.
    """
    services = [
        {"name": "Aurora UI", "port": 5000, "command": "npm run dev"},
        {"name": "Aurora Backend", "port": 5001, "command": "uvicorn aurora_x.serve:app"},
        {
            "name": "Learning Server",
            "port": 5002,
            "command": "python -m aurora_x.self_learn_server",
        },
        {"name": "Chat Server", "port": 8080, "command": "python -m aurora_x.chat.serve"},
    ]

    statuses = []
    for service in services:
        port_status = check_port_status(service["port"])

        status = ServiceStatus(
            name=service["name"],
            port=service["port"],
            status="running" if port_status["listening"] else "stopped",
            pid=port_status.get("pid"),
        )
        statuses.append(status)

    return {"services": statuses}


@router.post("/start/{service_name}")
async def start_service(service_name: str) -> dict[str, Any]:
    """
    Start a service using subprocess with proper background execution.
    Aurora supervises the startup.
    """
    # Map service names to commands and ports
    service_commands = {
        "aurora-ui": {
            "cwd": "/workspaces/Aurora-x/client",
            "cmd": ["npm", "run", "dev"],
            "port": 5000,
            "description": "Aurora UI (React + Vite)",
        },
        "aurora-backend": {
            "cwd": "/workspaces/Aurora-x",
            "cmd": [
                "uvicorn",
                "aurora_x.serve:app",
                "--host",
                "0.0.0.0",
                "--port",
                "5001",
                "--reload",
            ],
            "port": 5001,
            "description": "Aurora Backend API",
        },
        "learning-server": {
            "cwd": "/workspaces/Aurora-x",
            "cmd": ["python", "-m", "aurora_x.self_learn_server"],
            "port": 5002,
            "description": "Self-Learning Server",
        },
        "chat-server": {
            "cwd": "/workspaces/Aurora-x",
            "cmd": ["python", "-m", "aurora_x.chat.serve"],
            "port": 8080,
            "description": "Chat Server",
        },
    }

    if service_name not in service_commands:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    service = service_commands[service_name]

    # Check if service is already running
    port_status = check_port_status(service["port"])
    if port_status["listening"]:
        return {
            "success": False,
            "message": f"Service '{service_name}' is already running on port {service['port']}",
            "pid": port_status.get("pid"),
        }

    # Start service in background using subprocess
    try:
        # Use Popen for non-blocking background process
        process = subprocess.Popen(
            service["cmd"],
            cwd=service["cwd"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # Detach from parent process
        )

        return {
            "success": True,
            "message": f"Service '{service_name}' started successfully",
            "description": service["description"],
            "port": service["port"],
            "pid": process.pid,
            "note": "Service running in background. Check /api/services/status for status updates.",
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Command not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start service: {str(e)}")


@router.post("/stop/{service_name}")
async def stop_service(service_name: str) -> dict[str, Any]:
    """
    Stop a service by killing the process on its port.
    Aurora supervises the shutdown.
    """
    # Map service names to ports
    service_ports = {
        "aurora-ui": 5000,
        "aurora-backend": 5001,
        "learning-server": 5002,
        "chat-server": 8080,
    }

    if service_name not in service_ports:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    port = service_ports[service_name]

    # Check if service is running
    port_status = check_port_status(port)
    if not port_status["listening"]:
        return {
            "success": False,
            "message": f"Service '{service_name}' is not running on port {port}",
        }

    pid = port_status.get("pid")
    if not pid:
        raise HTTPException(
            status_code=500, detail=f"Could not determine PID for service on port {port}"
        )

    # Kill the process
    try:
        subprocess.run(["kill", "-TERM", str(pid)], check=True, timeout=5)

        return {
            "success": True,
            "message": f"Service '{service_name}' stopped successfully",
            "port": port,
            "pid": pid,
            "note": "Process terminated with SIGTERM",
        }
    except subprocess.CalledProcessError:
        # Try force kill if graceful shutdown fails
        try:
            subprocess.run(["kill", "-KILL", str(pid)], check=True, timeout=5)
            return {
                "success": True,
                "message": f"Service '{service_name}' force stopped",
                "port": port,
                "pid": pid,
                "note": "Process killed with SIGKILL (force)",
            }
        except Exception as kill_error:
            raise HTTPException(
                status_code=500, detail=f"Failed to stop service: {str(kill_error)}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop service: {str(e)}")


@router.post("/restart/{service_name}")
async def restart_service(service_name: str) -> dict[str, Any]:
    """
    Restart a service by stopping then starting it.
    Aurora supervises the restart.
    """
    if service_name not in ["aurora-ui", "aurora-backend", "learning-server", "chat-server"]:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

    results = {"stop": None, "start": None}

    # Stop the service first
    try:
        stop_result = await stop_service(service_name)
        results["stop"] = stop_result

        # Wait a moment for cleanup
        import asyncio

        await asyncio.sleep(1)
    except HTTPException as e:
        # Service might not be running, that's okay
        results["stop"] = {"success": False, "message": str(e.detail)}

    # Start the service
    try:
        start_result = await start_service(service_name)
        results["start"] = start_result

        return {
            "success": True,
            "message": f"Service '{service_name}' restarted successfully",
            "details": results,
        }
    except HTTPException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Service stopped but failed to restart: {str(e.detail)}",
            headers={"X-Restart-Details": str(results)},
        )


@router.post("/start-all")
async def start_all_services() -> dict[str, Any]:
    """
    Start all Aurora services.
    The big START ALL button!
    """
    services = ["aurora-backend", "learning-server", "chat-server", "aurora-ui"]
    results = {}

    for service_name in services:
        try:
            result = await start_service(service_name)
            results[service_name] = result
        except HTTPException as e:
            results[service_name] = {"success": False, "message": str(e.detail)}
        except Exception as e:
            results[service_name] = {"success": False, "message": str(e)}

    # Count successes
    successful = sum(1 for r in results.values() if r.get("success", False))

    return {
        "success": successful > 0,
        "message": f"Started {successful}/{len(services)} services",
        "services": results,
        "note": "Check individual service status at /api/services/status",
    }


# Export router
__all__ = ["router"]
