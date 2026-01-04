"""
Phase 4-6 Integration Validation Script
Tests SupervisorCore integration with Aurora Nexus V3
Note: Uses minimal workers to avoid thread limit issues when live supervisor is running
"""
import sys
import time
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "aurora_supervisor"))
sys.path.insert(0, str(ROOT))

from supervisor_core import AuroraSupervisor, KnowledgeFabric

print("[Validation] Testing AuroraSupervisor class instantiation ...")
core = AuroraSupervisor()
assert core is not None, "Failed to create AuroraSupervisor"
print("  AuroraSupervisor class instantiated correctly.")

print("[Validation] Testing KnowledgeFabric ...")
fabric = KnowledgeFabric()
assert fabric is not None, "Failed to create KnowledgeFabric"
print("  KnowledgeFabric instantiated correctly.")

print("[Validation] Checking knowledge fabric persistence ...")
snapshot_path = ROOT / "aurora_supervisor/data/knowledge/models/state_snapshot.json"
fabric.save_state()
assert snapshot_path.exists(), "Snapshot file missing after save_state()"
print("  Knowledge snapshot exists.")

print("[Validation] Testing reload of saved state ...")
fabric2 = KnowledgeFabric()
fabric2.load_state()
print("  Reload completed successfully.")

print("[Validation] Testing event recording ...")
fabric.record_event("test", "test/path", "Integration test event")
events_log = ROOT / "aurora_supervisor/data/knowledge/events.jsonl"
assert events_log.exists(), "Events log missing"
print("  Event recording works correctly.")

print("[Validation] Integration logic test: checking supervisor_integration module ...")
try:
    from aurora_nexus_v3.integrations.supervisor_integration import (
        start_supervisor,
        get_supervisor,
        attach_to_nexus_v3,
        get_supervisor_status
    )
    print("  Integration module imports successfully.")
    
    class MockNexus:
        supervisor = None
        def log(self, msg):
            print("[MockNexus]", msg)
    
    print("[Validation] Checking get_supervisor_status function ...")
    status = get_supervisor_status()
    print(f"  Supervisor status: {status}")
    
    if status.get("running"):
        print("  Live supervisor detected - verifying worker counts...")
        assert status.get("healers", 0) == 100, f"Expected 100 healers, found {status.get('healers')}"
        assert status.get("workers", 0) == 300, f"Expected 300 workers, found {status.get('workers')}"
        print("  Workers and healers verified (100 healers + 300 workers).")
    else:
        print("  No live supervisor detected (expected if running standalone test)")
    
    print("  Supervisor integration module validated.")
    
except Exception as e:
    raise AssertionError(f"Supervisor integration failed: {e}")

print("[Validation] Verifying supervisor data directories exist ...")
data_dir = ROOT / "aurora_supervisor/data"
knowledge_dir = data_dir / "knowledge"
models_dir = knowledge_dir / "models"
assert data_dir.exists(), "Data directory missing"
assert knowledge_dir.exists(), "Knowledge directory missing"
assert models_dir.exists(), "Models directory missing"
print("  All required directories exist.")

print("\n All Supervisor <-> Nexus V3 integration checks passed.")
