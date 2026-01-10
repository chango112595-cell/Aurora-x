"""
Luminar Nexus V2 Integration for Nexus V3
Connects "The Mouth" (Luminar V2) to "The Brain" (Nexus V3)
Enables direct Python communication without HTTP overhead
"""

import sys
from pathlib import Path
from typing import Any

AURORA_ROOT = Path(__file__).resolve().parents[2]
LUMINAR_PATH = AURORA_ROOT / "tools"

if str(LUMINAR_PATH) not in sys.path:
    sys.path.append(str(LUMINAR_PATH))

_luminar_instance = None
_nexus_v3_core = None


def get_luminar_instance():
    """Get the current Luminar Nexus V2 instance"""
    global _luminar_instance
    return _luminar_instance


def attach_luminar_to_nexus_v3(nexus_core, luminar_instance=None):
    """
    Connect Luminar Nexus V2 (The Mouth) to Aurora Nexus V3 (The Brain)

    Args:
        nexus_core: Aurora Nexus V3 core instance
        luminar_instance: Optional Luminar V2 instance (will start if None)

    Returns:
        bool: True if connection successful
    """
    global _luminar_instance, _nexus_v3_core

    _nexus_v3_core = nexus_core

    try:
        # If no instance provided, try to get existing one or start new
        if luminar_instance:
            _luminar_instance = luminar_instance
        else:
            # Try to import and get existing instance
            try:
                from luminar_nexus_v2 import LuminarNexusV2

                # Check if there's a global instance
                if hasattr(LuminarNexusV2, "_global_instance"):
                    _luminar_instance = LuminarNexusV2._global_instance
                else:
                    # Create new instance
                    _luminar_instance = LuminarNexusV2()
            except Exception as e:
                print(f"[Luminar Integration] Could not get Luminar instance: {e}")
                return False

        # Store reference in Nexus V3
        nexus_core.luminar_v2 = _luminar_instance

        # Store reference in Luminar V2
        if _luminar_instance:
            _luminar_instance.nexus_v3 = nexus_core
            print("[Luminar Integration] Luminar Nexus V2 connected to Aurora Nexus V3")
            print("[Luminar Integration] The Mouth -> The Brain connection established")
            return True

        return False

    except Exception as e:
        print(f"[Luminar Integration] Connection failed: {e}")
        return False


def send_to_nexus_v3(message: str, session_id: str = "default", context: Any = None) -> str | None:
    """
    Send a message from Luminar V2 to Nexus V3 for processing

    Args:
        message: The message to process
        session_id: Session identifier
        context: Optional context data

    Returns:
        Response string or None if Nexus V3 unavailable
    """
    global _nexus_v3_core

    if not _nexus_v3_core:
        return None

    try:
        # Use Nexus V3's Brain Bridge to process the message
        if hasattr(_nexus_v3_core, "brain_bridge") and _nexus_v3_core.brain_bridge:
            # Process through Brain Bridge (connects to Aurora Core Intelligence)
            import asyncio

            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Process message through Aurora Core Intelligence
            if (
                hasattr(_nexus_v3_core.brain_bridge, "aurora_core")
                and _nexus_v3_core.brain_bridge.aurora_core
            ):
                aurora_core = _nexus_v3_core.brain_bridge.aurora_core
                if hasattr(aurora_core, "process_conversation"):
                    response = loop.run_until_complete(
                        aurora_core.process_conversation(message, session_id)
                    )
                    return response

            # Fallback: Use Nexus V3's task dispatcher
            if hasattr(_nexus_v3_core, "task_dispatcher") and _nexus_v3_core.task_dispatcher:
                from aurora_nexus_v3.workers.worker import Task, TaskType

                task = Task(
                    id=f"luminar_chat_{session_id}",
                    task_type=TaskType.CUSTOM,
                    payload={
                        "message": message,
                        "session_id": session_id,
                        "context": context,
                        "source": "luminar_v2",
                    },
                    priority=5,
                )

                # Dispatch task (this is async, but we'll handle it)
                loop.run_until_complete(_nexus_v3_core.task_dispatcher.dispatch(task))

                # Return confirmation that message was routed to Nexus V3
                # Note: Task execution is asynchronous - result will be processed by workers
                return f"Message routed to Nexus V3 for processing: {message[:50]}..."

        return None

    except Exception as e:
        print(f"[Luminar Integration] Error sending to Nexus V3: {e}")
        return None


def get_luminar_status() -> dict[str, Any]:
    """Get Luminar Nexus V2 status for monitoring"""
    global _luminar_instance

    if _luminar_instance:
        try:
            return {
                "connected": True,
                "version": getattr(_luminar_instance, "version", "2.0.0"),
                "quantum_coherence": getattr(_luminar_instance, "quantum_mesh", {}).get(
                    "coherence_level", 0.0
                ),
                "services": len(getattr(_luminar_instance, "service_registry", {})),
                "monitoring_active": getattr(_luminar_instance, "monitoring_active", False),
            }
        except Exception as e:
            return {"connected": True, "error": str(e)}

    return {"connected": False, "error": "Luminar V2 not initialized"}
