#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.coordinator import Coordinator


def test_coordinator_no_profile(tmp_path):
    profile_path = tmp_path / "nonexistent.json"
    coord = Coordinator(profile_path=str(profile_path))
    assert coord.profile == {}
    assert coord.get_recommended_mode() == "python"
    assert coord.has_gpu() == False


def test_coordinator_with_profile(tmp_path):
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(
        json.dumps(
            {
                "summary": {"recommended_mode": "hybrid", "score": 85},
                "gpu": {"has_nvidia": True, "has_amd": False},
            }
        )
    )
    coord = Coordinator(profile_path=str(profile_path))
    assert coord.get_recommended_mode() == "hybrid"
    assert coord.get_device_score() == 85
    assert coord.has_gpu() == True
    assert coord.should_enable("hybrid") == True
    assert coord.should_enable("python") == False
