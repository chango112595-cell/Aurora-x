#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_runtime_loader_basic(tmp_path):
    # smoke test: create a tiny python script in pack vfs and run
    from core.runtime_loader import RuntimeLoader
    from core.vfs import VirtualFS

    pack = "test_runtime_pack"
    vfs = VirtualFS(pack)
    # Write script into the VFS
    vfs.write_text("hello.py", "print('hello from python')")
    rl = RuntimeLoader(pack)
    # Run with just the filename (relative to vfs root)
    r = rl.run("hello.py")
    assert r.get("rc", 0) == 0
