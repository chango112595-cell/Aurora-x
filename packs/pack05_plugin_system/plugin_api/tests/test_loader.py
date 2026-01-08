#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.loader import PluginLoader


def test_stage_package(tmp_path):
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "manifest.json").write_text(
        __import__("json").dumps(
            {"id": "acme.test", "name": "T", "version": "0.1.0", "entrypoint": "main.py"}
        )
    )
    (pkg / "main.py").write_text("print('hi')")
    pl = PluginLoader()
    res = pl.stage_package(str(pkg))
    assert res["ok"] is True
    from core.registry import PluginRegistry

    PluginRegistry().unregister("acme.test")
