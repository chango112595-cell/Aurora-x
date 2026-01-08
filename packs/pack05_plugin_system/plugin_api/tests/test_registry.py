#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.registry import PluginRegistry


def test_registry_register_and_get(tmp_path):
    man = {"id": "acme.echo", "name": "Echo", "version": "0.0.1", "entrypoint": "echo.py"}
    d = tmp_path / "pkg"
    d.mkdir()
    (d / "manifest.json").write_text(__import__("json").dumps(man))
    pr = PluginRegistry()
    assert pr.register(man, ["manifest.json"]) is True
    assert pr.get("acme.echo")["manifest"]["name"] == "Echo"
    pr.unregister("acme.echo")
