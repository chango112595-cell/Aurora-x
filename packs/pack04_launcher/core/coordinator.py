#!/usr/bin/env python3
"""
coordinator.py - coordinate launch ordering and cross-pack signals.
Example: when pack02 profile reports GPU available, start GPU jobs.
"""

import json
from pathlib import Path

LIVE_ENV = Path("live") / "environment" / "profile.json"


class Coordinator:
    def __init__(self, profile_path=None):
        self.profile_path = Path(profile_path) if profile_path else LIVE_ENV
        self.profile = self._load_profile()

    def _load_profile(self):
        if self.profile_path.exists():
            return json.loads(self.profile_path.read_text())
        return {}

    def reload_profile(self):
        self.profile = self._load_profile()

    def should_enable(self, feature):
        """Check if a feature should be enabled based on profile."""
        recommended = self.profile.get("summary", {}).get("recommended_mode")
        return recommended == feature

    def has_gpu(self):
        """Check if GPU is available."""
        gpu = self.profile.get("gpu", {})
        return gpu.get("has_nvidia", False) or gpu.get("has_amd", False)

    def get_recommended_mode(self):
        """Get the recommended execution mode."""
        return self.profile.get("summary", {}).get("recommended_mode", "python")

    def get_device_score(self):
        """Get the device capability score."""
        return self.profile.get("summary", {}).get("score", 0)
