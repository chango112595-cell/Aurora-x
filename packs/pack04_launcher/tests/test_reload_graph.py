#!/usr/bin/env python3
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.reload_graph import build_graph, topo_order, get_reload_order

def test_build_graph(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({
        "jobs": [
            {"name": "a", "cmd": "echo a", "depends_on": []},
            {"name": "b", "cmd": "echo b", "depends_on": ["a"]},
            {"name": "c", "cmd": "echo c", "depends_on": ["a", "b"]}
        ]
    }))
    graph = build_graph(str(manifest_path))
    assert "a" in graph
    assert "b" in graph
    assert "c" in graph
    assert graph["a"] == []
    assert graph["b"] == ["a"]

def test_topo_order():
    graph = {"a": [], "b": ["a"], "c": ["b"]}
    order = topo_order(graph)
    assert order.index("a") < order.index("b")
    assert order.index("b") < order.index("c")

def test_empty_graph():
    assert topo_order({}) == []
    assert build_graph("/nonexistent") == {}
