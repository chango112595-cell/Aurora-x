"""
FastAPI Command Control Router
- Web API for Aurora Unified Command Manager
- Called from the button interface
- Supports both sync and async operations
"""

import sys
from pathlib import Path

from fastapi import APIRouter, WebSocket
from pydantic import BaseModel

# Import our unified command manager
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from aurora_unified_cmd import AuroraCommandManager
except ImportError:
    # Fallback if module not in path
    import sys
    from pathlib import Path
    root = Path(__file__).parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        from aurora_unified_cmd import AuroraCommandManager
    except ImportError:
        AuroraCommandManager = None

router = APIRouter(prefix="/api/commands", tags=["commands"])
manager = AuroraCommandManager()


class CommandRequest(BaseModel):
    """Request model for commands"""

    command: str
    args: list = []


@router.post("/start")
async def start_system():
    """Start complete Aurora system"""
    result = manager.startup_full_system()
    return result


@router.post("/stop")
async def stop_system():
    """Stop all Aurora services"""
    result = manager.cleanup_system()
    return {"status": "stopped", "success": result}


@router.get("/status")
async def get_status():
    """Get system status"""
    return manager.get_system_status()


@router.get("/health")
async def get_health():
    """Check service health"""
    return manager.check_system_health()


@router.post("/fix")
async def trigger_fix():
    """Have Aurora fix herself"""
    return manager.run_aurora_auto_fix()


@router.post("/test")
async def run_tests():
    """Run all tests"""
    return manager.run_all_tests()


@router.get("/logs")
async def get_logs(lines: int = 50):
    """Get command logs"""
    logs = manager.view_logs(lines)
    return {"logs": logs}


@router.post("/command")
async def execute_command(req: CommandRequest):
    """Generic command executor"""
    result = manager.parse_command(req.command, req.args)
    return result


@router.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    """WebSocket for real-time status updates"""
    await websocket.accept()
    try:
        while True:
            # Send health status every 2 seconds
            import asyncio

            await asyncio.sleep(2)
            health = manager.check_system_health()
            await websocket.send_json(health)
    except Exception:
        pass
    finally:
        await websocket.close()
