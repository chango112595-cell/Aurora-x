#!/usr/bin/env python3
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.supervisor import Supervisor, Job, JobPolicy

def test_supervisor_start_stop(tmp_path):
    metrics_path = tmp_path / "metrics.json"
    s = Supervisor(metrics_path=str(metrics_path))
    # fake job spec
    res = s.start_job({"name": "unittest_job", "cmd": "echo hi"})
    assert isinstance(res, dict)
    assert "rc" in res or "error" in res
    # stop (best-effort)
    stop_res = s.stop_job("unittest_job")
    assert isinstance(stop_res, dict)
    s.stop()
    time.sleep(0.1)

def test_job_policy():
    policy = JobPolicy(max_restarts=5, backoff_seconds=1)
    assert policy.max_restarts == 5
    assert policy.backoff_seconds == 1

def test_job_creation():
    job = Job("test_job", "echo test")
    assert job.name == "test_job"
    assert job.cmd == "echo test"
    assert job._restarts == 0

def test_supervisor_list_jobs(tmp_path):
    metrics_path = tmp_path / "metrics.json"
    s = Supervisor(metrics_path=str(metrics_path))
    s.start_job({"name": "job1", "cmd": "echo 1"})
    s.start_job({"name": "job2", "cmd": "echo 2"})
    jobs = s.list_jobs()
    assert "job1" in jobs
    assert "job2" in jobs
    s.stop()
