"""
Aurora Supervisor Integration for Nexus V3
Phase 4-6 Controller Integration
"""
import os
import sys
import threading
import time
from pathlib import Path

AURORA_ROOT = Path(__file__).resolve().parents[2]
SUPERVISOR_PATH = AURORA_ROOT / "aurora_supervisor"

if str(SUPERVISOR_PATH) not in sys.path:
    sys.path.append(str(SUPERVISOR_PATH))

_supervisor_instance = None


def start_supervisor():
    """Start the Aurora Supervisor in a daemon thread"""
    global _supervisor_instance
    try:
        from supervisor_core import AuroraSupervisor
        
        _supervisor_instance = AuroraSupervisor()
        
        def run_supervisor():
            try:
                _supervisor_instance.start()
            except Exception as e:
                print(f"[Integration] Supervisor thread error: {e}")
        
        t = threading.Thread(target=run_supervisor, daemon=True, name="AuroraSupervisor")
        t.start()
        print("[Integration] AuroraSupervisor launched successfully.")
        return _supervisor_instance
    except Exception as e:
        print(f"[Integration] Failed to start AuroraSupervisor: {e}")
        return None


def get_supervisor():
    """Get the current supervisor instance"""
    return _supervisor_instance


def attach_to_nexus_v3(nexus_server):
    """
    Called during Aurora Nexus V3 boot sequence.
    Provides Nexus with SupervisorCore reference and hooks.
    """
    supervisor = start_supervisor()
    if supervisor:
        nexus_server.supervisor = supervisor
        print("[NexusV3] SupervisorCore attached.")
        return True
    return False


def get_supervisor_status():
    """Get supervisor status for monitoring"""
    if _supervisor_instance:
        return {
            "running": _supervisor_instance.running,
            "healers": len(_supervisor_instance.healers),
            "workers": len(_supervisor_instance.workers),
            "memory_keys": list(_supervisor_instance.fabric.memory.keys())[:10]
        }
    return {"running": False, "error": "Supervisor not initialized"}
