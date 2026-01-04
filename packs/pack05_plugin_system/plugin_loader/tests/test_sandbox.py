#!/usr/bin/env python3
import time, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from loader.sandbox_runtime import SandboxRuntime

def test_sandbox_stage_and_run(tmp_path):
    pkg = tmp_path / "mypkg"
    pkg.mkdir()
    (pkg / "manifest.json").write_text(__import__("json").dumps({"id":"acme.testpkg","name":"T","version":"0.1.0","entrypoint":"run.sh"}))
    (pkg / "run.sh").write_text("#!/bin/sh\necho hello-sandbox\n")
    sr = SandboxRuntime("acme.testpkg")
    assert sr.stage_package(str(pkg)) is True
    res = sr.run_entry("sh run.sh", timeout=5)
    assert res.get("rc", 0) == 0
    assert "hello-sandbox" in res.get("stdout","")
