from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from aurora_x.corpus.store import record, spec_digest


def _seed(tmp: Path, name="add", snippet="def add(a,b): return a+b"):
    entry = {
        "func_name": name,
        "func_signature": f"{name}(a:int,b:int)->int",
        "passed": 3, "total": 3, "score": 0.0,
        "snippet": snippet, **spec_digest("#")
    }
    record(tmp/"run-dump", entry)

def test_dump_grep_and_json():
    tmp = Path(tempfile.mkdtemp())
    _seed(tmp, "add", "def add(a,b): return a+b")
    _seed(tmp, "add", "def add(a,b): return a-b  # variant")
    cmd = [
        sys.executable, "-m", "aurora_x.main",
        "--dump-corpus", "add(a:int,b:int)->int",
        "--outdir", str(tmp),
        "--top", "10",
        "--grep", "variant",
        "--json"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    arr = json.loads(proc.stdout)
    assert len(arr) >= 1
    assert any("variant" in (r.get("snippet") or "") for r in arr)
