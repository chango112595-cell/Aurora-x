import tempfile
from pathlib import Path
from aurora_x.corpus.store import record, retrieve, spec_digest

def test_record_and_retrieve():
    root = Path(tempfile.mkdtemp())
    dig = spec_digest("# spec\n- name: add")
    entry = {
        "func_name": "add",
        "func_signature": "add(a:int,b:int)->int",
        "passed": 3, "total": 3, "score": 0.0,
        "snippet": "def add(a,b): return a+b", **dig
    }
    record(root, entry)
    rows = retrieve(root, "add(a:int,b:int)->int", k=1)
    assert rows and rows[0]["func_name"] == "add"