#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.lifecycle import ModuleLifecycle


def test_lifecycle_load_activate(tmp_path):
    pack = "testmodpack"
    src = tmp_path / "mod"
    src.mkdir()
    f = src / "hello.py"
    f.write_text("print('hi')")
    m = ModuleLifecycle(pack)
    assert m.load_from_dir(str(src))
    res = m.activate("python3 hello.py", background=False)
    assert res.get("rc", 0) == 0
