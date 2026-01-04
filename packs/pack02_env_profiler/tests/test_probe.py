#!/usr/bin/env python3
import json
import subprocess


def test_probe_safe():
    out = subprocess.check_output(
        ["python3", "packs/pack02_env_profiler/profiler/device_probe.py", "--safe"]
    )
    j = json.loads(out)
    assert "basic" in j
    assert "machine" in j["basic"] or "python_version" in j["basic"]
