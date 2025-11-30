#!/usr/bin/env python3
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.orchestrator import Orchestrator

def test_orchestrator_list_jobs(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({
        "jobs": [
            {"name": "job1", "cmd": "echo 1"},
            {"name": "job2", "cmd": "echo 2"}
        ]
    }))
    orch = Orchestrator(manifest_path=str(manifest_path))
    jobs = orch.list_jobs()
    assert "job1" in jobs
    assert "job2" in jobs

def test_orchestrator_get_job(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({
        "jobs": [{"name": "test_job", "cmd": "echo test"}]
    }))
    orch = Orchestrator(manifest_path=str(manifest_path))
    job = orch.get_job("test_job")
    assert job is not None
    assert job["name"] == "test_job"
    
    missing = orch.get_job("nonexistent")
    assert missing is None

def test_orchestrator_reload(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"jobs": []}))
    orch = Orchestrator(manifest_path=str(manifest_path))
    assert orch.list_jobs() == []
    
    manifest_path.write_text(json.dumps({"jobs": [{"name": "new_job", "cmd": "echo new"}]}))
    orch.reload_manifest()
    assert "new_job" in orch.list_jobs()
