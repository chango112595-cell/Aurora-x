"""
Aurora Nexus V3 Main Entry Point
Starts the full AuroraUniversalCore with all systems wired together:
- 300 Autonomous Workers
- 188 Tiers | 66 AEMs | 550 Modules
- Brain Bridge (Aurora Core Intelligence)
- Supervisor (100 healers + 300 workers)
- Luminar V2 Integration
- All core modules (Port Manager, Service Registry, API Gateway, etc.)
"""

import os
import time

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from aurora_nexus_v3.core.universal_core import AuroraUniversalCore

APP_TOKEN = os.environ.get("AURORA_API_TOKEN", None)

app = FastAPI(title="Aurora Nexus V3 - Universal Consciousness Engine")
core: AuroraUniversalCore | None = None


class ExecRequest(BaseModel):
    module: str
    action: str
    payload: dict = {}


@app.on_event("startup")
async def startup():
    """Initialize Aurora Universal Core with all systems"""
    global core
    try:
        core = AuroraUniversalCore()
        await core.start()

        # Enable hybrid mode to activate all capabilities
        await core.enable_hybrid_mode()

        print("\n" + "=" * 80)
        print("[OK] AURORA NEXUS V3 FULLY OPERATIONAL")
        print("=" * 80)
        print(f"   - {core.WORKER_COUNT} Autonomous Workers")
        print(f"   - {core.TIER_COUNT} Tiers | {core.AEM_COUNT} AEMs | {core.MODULE_COUNT} Modules")
        bridge_status = (
            "Connected" if core.brain_bridge and core.brain_bridge.initialized else "Disconnected"
        )
        print(f"   - Brain Bridge: {bridge_status}")
        print(f"   - Supervisor: {'Connected' if core.supervisor else 'Disconnected'}")
        print(f"   - Luminar V2: {'Connected' if core.luminar_v2 else 'Disconnected'}")
        print(f"   - Hybrid Mode: {'ENABLED' if core.hybrid_mode_enabled else 'DISABLED'}")
        print("=" * 80 + "\n")
    except Exception as e:
        print(f"[ERROR] Failed to start Aurora Nexus V3: {e}")
        raise RuntimeError(f"Failed to initialize Aurora Universal Core: {e}") from e


@app.on_event("shutdown")
async def shutdown():
    """Shutdown Aurora Universal Core"""
    if core:
        try:
            await core.stop()
        except Exception as e:
            print(f"Warning during shutdown: {e}")


def require_token(token: str | None):
    if APP_TOKEN and token != APP_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/health")
async def health():
    """Health check endpoint"""
    if not core:
        return {"ok": False, "error": "Core not initialized"}
    return {
        "ok": core.state.value == "running",
        "version": core.VERSION,
        "codename": core.CODENAME,
        "state": core.state.value,
    }


@app.get("/status")
async def status():
    """Get full system status"""
    if not core:
        raise HTTPException(status_code=503, detail="Core not initialized")
    return core.get_status()


@app.get("/modules")
async def modules():
    """List all loaded modules"""
    if not core:
        raise HTTPException(status_code=503, detail="Core not initialized")
    return {
        "core_modules": list(core.modules.keys()),
        "module_count": len(core.modules),
        "manifest_modules": (
            core.manifest_integrator.module_count if core.manifest_integrator else 0
        ),
    }


@app.post("/execute")
async def execute(req: ExecRequest, token: str | None = None):
    """Execute a task through the hybrid orchestrator"""
    require_token(token)
    if not core or not core.hybrid_orchestrator:
        raise HTTPException(status_code=503, detail="Hybrid orchestrator not available")

    result = await core.execute_hybrid_task(
        task_type=req.action,
        payload=req.payload,
    )

    if result is None:
        raise HTTPException(status_code=400, detail="Task execution failed")

    return result


@app.get("/api/workers/status")
async def get_worker_status():
    """Get worker pool status"""
    if not core or not core.worker_pool:
        return {"error": "Worker pool not initialized", "workers": 0, "queued": 0}

    metrics = core.worker_pool.get_metrics()
    return {
        "total_workers": metrics.total_workers,
        "active_workers": metrics.active_workers,
        "idle_workers": metrics.idle_workers,
        "tasks_queued": metrics.tasks_queued,
        "tasks_completed": metrics.tasks_completed,
        "tasks_failed": metrics.tasks_failed,
    }


@app.post("/api/process")
async def process_request(request_data: dict):
    """
    Process natural language requests and route to workers.
    This is the main endpoint for handling user requests like
    "analyze my windows and make it better"
    """
    if not core:
        raise HTTPException(status_code=503, detail="Core not initialized")

    request_text = (
        request_data.get("input") or request_data.get("request") or request_data.get("message", "")
    )
    request_type = request_data.get("type", "conversation")
    session_id = request_data.get("session_id", "default")

    if not request_text:
        raise HTTPException(status_code=400, detail="Request text is required")

    # Route to task dispatcher for actual execution
    if core.task_dispatcher:
        from aurora_nexus_v3.workers.worker import Task, TaskType

        # Determine task type from request
        request_lower = request_text.lower()
        if any(word in request_lower for word in ["analyze", "check", "scan", "examine"]):
            task_type = TaskType.ANALYZE
        elif any(word in request_lower for word in ["fix", "repair", "heal", "resolve"]):
            task_type = TaskType.FIX
        elif any(word in request_lower for word in ["optimize", "improve", "enhance", "better"]):
            task_type = TaskType.OPTIMIZE
        elif any(word in request_lower for word in ["create", "build", "generate", "make"]):
            task_type = TaskType.CODE
        else:
            task_type = TaskType.CUSTOM

        task = Task(
            id=f"request_{session_id}_{int(time.time())}",
            task_type=task_type,
            payload={
                "request": request_text,
                "type": request_type,
                "session_id": session_id,
                "source": "api_process",
            },
            priority=1,  # High priority for user requests
        )

        # Dispatch task
        task_id = await core.task_dispatcher.dispatch(task)

        # Return immediate response
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Request queued for execution: {request_text[:100]}...",
            "status": "processing",
            "workers_available": (
                core.worker_pool.get_metrics().idle_workers if core.worker_pool else 0
            ),
        }

    # Fallback if task dispatcher not available
    return {
        "success": False,
        "message": "Task dispatcher not available",
        "request": request_text,
    }


def main():
    """Main entry point"""
    port = int(os.getenv("AURORA_NEXUS_PORT", "5002"))
    host = os.getenv("AURORA_NEXUS_HOST", "0.0.0.0")

    print(f"\n[AURORA] Starting Aurora Nexus V3 on {host}:{port}")
    print("   This will initialize ALL systems:\n")
    print("   - 300 Autonomous Workers")
    print("   - 188 Tiers | 66 AEMs | 550 Modules")
    print("   - Brain Bridge (Aurora Core Intelligence)")
    print("   - Supervisor (100 healers + 300 workers)")
    print("   - Luminar V2 Integration")
    print("   - All Core Modules\n")

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
