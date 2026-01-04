#!/usr/bin/env python3
"""
supervisor.py - Supervisor system for launching and monitoring jobs.
Features:
- start/stop jobs
- restart on failure based on policy (max_restarts, backoff)
- health probes
- conservative default policies (no forced kills unless explicit)
- Track spawned process handles for reliable stop/restart
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
    def __init__(self, name, cmd, pack="pack04_launcher", policy=None, runtime=None):
        self.name = name
        self.cmd = cmd
        self.pack = pack
        self.policy = policy or JobPolicy()
        self.runtime = runtime or "python"
        self.rt = PackProcess(pack, workdir=str(ROOT / "data" / "vfs" / name))
        self._proc = None
        self._pid = None
        self._restarts = 0

class Supervisor:
    _instance = None
    _lock_class = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock_class:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, metrics_path=None):
        if self._initialized:
            return
        self._initialized = True
        self.jobs = {}  # name -> Job
        self._pids = {}  # name -> pid (tracked process handles)
        self._lock = threading.Lock()
        self._metrics = Metrics(metrics_path) if metrics_path else Metrics()
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    @classmethod
    def reset_instance(cls):
        """Reset singleton for testing purposes."""
        with cls._lock_class:
            if cls._instance:
                cls._instance._running = False
                cls._instance = None

    def register_job(self, job: Job):
        with self._lock:
            self.jobs[job.name] = job
        return True

    def start_job(self, job_spec):
        name = job_spec.get("name")
        cmd = job_spec.get("cmd")
        runtime = job_spec.get("runtime", "python")
        if not name or not cmd:
            return {"error": "job spec missing name or cmd"}
        job = Job(name, cmd, runtime=runtime)
        self.register_job(job)
        res = self._start(job)
        return res

    def _start(self, job: Job):
        out = job.rt.run(job.cmd, timeout=60)
        self._metrics.record(job.name, out.get("rc", -1))
        return out

    def start_background(self, job_spec):
        """Start a job in background and track its PID."""
        name = job_spec.get("name")
        cmd = job_spec.get("cmd")
        if not name or not cmd:
            return {"error": "job spec missing name or cmd"}
        job = Job(name, cmd)
        self.register_job(job)
        pid = job.rt.run_background(cmd)
        with self._lock:
            self._pids[name] = pid
        self._metrics.record(name, 0)
        return {"pid": pid, "name": name}

    def stop_job(self, name: str):
        """Stop a job using tracked PID or best-effort process lookup."""
        stopped = []
        with self._lock:
            if name in self._pids:
                pid = self._pids[name]
                try:
                    os.kill(pid, 15)
                    stopped.append(str(pid))
                    del self._pids[name]
                except (ProcessLookupError, PermissionError):
                    pass
            if name in self.jobs:
                del self.jobs[name]
        
        if not stopped:
            job = self.jobs.get(name)
            cmd_pattern = job.cmd if job else name
            pids = subprocess.getoutput(f"pgrep -f '{cmd_pattern}'").strip().splitlines()
            for pid in pids:
                try:
                    os.kill(int(pid), 15)
                    stopped.append(pid)
                except (ValueError, ProcessLookupError, PermissionError):
                    pass
        return {"stopped": stopped}

    def list_jobs(self):
        with self._lock:
            return list(self.jobs.keys())

    def get_pids(self):
        with self._lock:
            return dict(self._pids)

    def stop(self):
        self._running = False

    def stop_all(self):
        """Stop all tracked jobs."""
        with self._lock:
            names = list(self.jobs.keys())
        results = {}
        for name in names:
            results[name] = self.stop_job(name)
        return results

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
