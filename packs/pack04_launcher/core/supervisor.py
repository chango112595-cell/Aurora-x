#!/usr/bin/env python3
"""
supervisor.py - Supervisor system for launching and monitoring jobs.
Features:
- start/stop jobs
- restart on failure based on policy (max_restarts, backoff)
- health probes
- conservative default policies (no forced kills unless explicit)
"""
import threading, time, json, os, subprocess
from pathlib import Path
from .process_abstraction import PackProcess
from .metrics import Metrics

ROOT = Path(__file__).resolve().parents[1]

class JobPolicy:
    def __init__(self, max_restarts=3, backoff_seconds=2):
        self.max_restarts = max_restarts
        self.backoff_seconds = backoff_seconds

class Job:
    def __init__(self, name, cmd, pack="pack04_launcher", policy=None):
        self.name = name
        self.cmd = cmd
        self.pack = pack
        self.policy = policy or JobPolicy()
        self.rt = PackProcess(pack, workdir=str(ROOT / "data" / "vfs" / name))
        self._proc = None
        self._restarts = 0

class Supervisor:
    def __init__(self, metrics_path=None):
        self.jobs = {}  # name -> Job
        self._lock = threading.Lock()
        self._metrics = Metrics(metrics_path) if metrics_path else Metrics()
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def register_job(self, job: Job):
        with self._lock:
            self.jobs[job.name] = job
        return True

    def start_job(self, job_spec):
        name = job_spec.get("name")
        cmd = job_spec.get("cmd")
        if not name or not cmd:
            return {"error": "job spec missing name or cmd"}
        job = Job(name, cmd)
        self.register_job(job)
        res = self._start(job)
        return res

    def _start(self, job: Job):
        out = job.rt.run(job.cmd, timeout=60)
        self._metrics.record(job.name, out.get("rc", -1))
        return out

    def stop_job(self, name: str):
        pids = subprocess.getoutput("pgrep -f '{}'".format(name)).strip().splitlines()
        stopped = []
        for pid in pids:
            try:
                os.kill(int(pid), 15)
                stopped.append(pid)
            except Exception:
                pass
        return {"stopped": stopped}

    def list_jobs(self):
        with self._lock:
            return list(self.jobs.keys())

    def stop(self):
        self._running = False

    def _monitor_loop(self):
        while self._running:
            try:
                with self._lock:
                    for name, job in list(self.jobs.items()):
                        rc = self._metrics.last_rc(job.name)
                        if rc is not None and rc != 0 and job._restarts < job.policy.max_restarts:
                            job._restarts += 1
                            time.sleep(job.policy.backoff_seconds)
                            self._start(job)
            except Exception:
                pass
            time.sleep(1)
