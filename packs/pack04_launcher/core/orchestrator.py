#!/usr/bin/env python3
"""
orchestrator.py - orchestrates jobs defined in a launch manifest.
Jobs contain name, cmd, pack, retries, runtime hints.
Interacts with shared Supervisor and RuntimeLoader for cross-runtime support.
"""
import json
from pathlib import Path
from .supervisor import Supervisor, Job
from .runtime_loader import RuntimeLoader

ROOT = Path(__file__).resolve().parents[1]
LAUNCH_MANIFEST = ROOT / "data" / "launch_manifest.json"

class Orchestrator:
    def __init__(self, manifest_path=None, supervisor=None):
        self.manifest_path = Path(manifest_path) if manifest_path else LAUNCH_MANIFEST
        self.manifest = self._load_manifest()
        self._sup = supervisor
        self._runtime_loader = RuntimeLoader()

    @property
    def sup(self):
        if self._sup is None:
            self._sup = Supervisor()
        return self._sup

    def set_supervisor(self, supervisor):
        """Set shared supervisor instance."""
        self._sup = supervisor

    def _load_manifest(self):
        if self.manifest_path.exists():
            return json.loads(self.manifest_path.read_text())
        return {"jobs": []}

    def reload_manifest(self):
        self.manifest = self._load_manifest()

    def list_jobs(self):
        return [j.get("name") for j in self.manifest.get("jobs", [])]

    def get_job(self, name):
        for j in self.manifest.get("jobs", []):
            if j.get("name") == name:
                return j
        return None

    def _determine_runtime(self, job_spec):
        """Determine runtime from job spec or use RuntimeLoader to choose."""
        if "runtime" in job_spec:
            return job_spec["runtime"]
        return self._runtime_loader.choose_runtime()

    def start_job(self, name):
        """Start a job with proper runtime selection."""
        job_spec = self.get_job(name)
        if not job_spec:
            return {"error": "job not found"}
        
        runtime = self._determine_runtime(job_spec)
        job_spec_with_runtime = {**job_spec, "runtime": runtime}
        
        cmd = job_spec.get("cmd", "")
        target = job_spec.get("target")
        
        if target:
            if runtime == "python":
                result = self._runtime_loader.run_python(target)
            elif runtime == "node":
                result = self._runtime_loader.run_node(target)
            else:
                result = self._runtime_loader.run(target)
            return result
        else:
            return self.sup.start_job(job_spec_with_runtime)

    def stop_job(self, name):
        return self.sup.stop_job(name)

    def start_all(self):
        """Start all jobs from manifest with proper runtime selection."""
        results = {}
        for j in self.manifest.get("jobs", []):
            name = j.get("name")
            results[name] = self.start_job(name)
        return results

    def stop_all(self):
        return self.sup.stop_all()
