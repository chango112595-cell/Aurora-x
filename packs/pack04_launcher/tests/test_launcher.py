#!/usr/bin/env python3
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.supervisor import Supervisor
from core.launcher import LauncherCLI, load_manifest

def test_load_manifest_empty():
    # ensure manifest absent returns empty
    m = load_manifest("/nonexistent/path")
    assert isinstance(m, dict)
    assert "jobs" in m
    assert m["jobs"] == []

def test_launcher_list_empty(tmp_path):
    Supervisor.reset_instance()
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"jobs": []}))
    lc = LauncherCLI(manifest_path=str(manifest_path))
    result = lc.list()
    assert isinstance(result, list)
    assert result == []
    lc.shutdown()

def test_launcher_list_with_jobs(tmp_path):
    Supervisor.reset_instance()
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({
        "jobs": [
            {"name": "job1", "cmd": "echo 1"},
            {"name": "job2", "cmd": "echo 2"}
        ]
    }))
    lc = LauncherCLI(manifest_path=str(manifest_path))
    result = lc.list()
    assert "job1" in result
    assert "job2" in result
    lc.shutdown()

def test_launcher_start_nonexistent(tmp_path):
    Supervisor.reset_instance()
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"jobs": []}))
    lc = LauncherCLI(manifest_path=str(manifest_path))
    result = lc.start("nonexistent")
    assert "error" in result
    lc.shutdown()

def test_launcher_shared_supervisor(tmp_path):
    Supervisor.reset_instance()
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({
        "jobs": [{"name": "test", "cmd": "echo test"}]
    }))
    lc = LauncherCLI(manifest_path=str(manifest_path))
    # LauncherCLI and Orchestrator should share the same supervisor
    assert lc.sup is lc.orch.sup
    lc.shutdown()
