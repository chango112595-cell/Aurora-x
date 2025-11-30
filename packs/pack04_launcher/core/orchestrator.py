#!/usr/bin/env python3
"""
orchestrator.py - orchestrates jobs defined in a launch manifest.
Jobs contain name, cmd, pack, retries, runtime hints.
Interacts with Supervisor and RuntimeLoader.
"""
import json
from pathlib import Path
from .supervisor import Supervisor, Job
from .runtime_loader import RuntimeLoader

ROOT = Path(__file__).resolve().parents[1]
LAUNCH_MANIFEST = ROOT / "data" / "launch_manifest.json"

class Orchestrator:
    def __init__(self, manifest_path=None):
        self.manifest_path = Path(manifest_path) if manifest_path else LAUNCH_MANIFEST
        self.manifest = self._load_manifest()
        self._sup = None

    @property
    def sup(self):
        if self._sup is None:
            self._sup = Supervisor()
        return self._sup

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

    def start_job(self, name):
        job = self.get_job(name)
        if not job:
            return {"error": "job not found"}
        return self.sup.start_job(job)

    def stop_job(self, name):
        return self.sup.stop_job(name)

    def start_all(self):
        results = {}
        for j in self.manifest.get("jobs", []):
            name = j.get("name")
            results[name] = self.sup.start_job(j)
        return results
