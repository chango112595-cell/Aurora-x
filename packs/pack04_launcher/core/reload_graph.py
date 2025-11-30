#!/usr/bin/env python3
"""
reload_graph.py - constructs a dependency graph from the launch manifest and
supports runtime hot-reload ordering (topological ordering).
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
LAUNCH_MANIFEST = ROOT / "data" / "launch_manifest.json"

def build_graph(manifest_path=None):
    """Build dependency graph from launch manifest."""
    path = Path(manifest_path) if manifest_path else LAUNCH_MANIFEST
    if not path.exists():
        return {}
    m = json.loads(path.read_text())
    jobs = {j["name"]: j for j in m.get("jobs", [])}
    graph = {}
    for n, j in jobs.items():
        deps = j.get("depends_on", [])
        graph[n] = deps
    return graph

def topo_order(graph):
    """Topological sort using Kahn's algorithm.
    Returns nodes in dependency order (dependencies first).
    """
    if not graph:
        return []
    
    # Build reverse adjacency (who depends on whom)
    indeg = {n: 0 for n in graph}
    for n, deps in graph.items():
        for d in deps:
            if d in graph:
                indeg[n] += 1
    
    # Start with nodes that have no dependencies
    q = [n for n, deg in indeg.items() if deg == 0]
    order = []
    
    while q:
        n = q.pop(0)
        order.append(n)
        # Find all nodes that depend on n and reduce their indegree
        for m, deps in graph.items():
            if n in deps and m not in order:
                indeg[m] -= 1
                if indeg[m] == 0:
                    q.append(m)
    
    return order

def get_reload_order(manifest_path=None):
    """Get the proper reload order for jobs based on dependencies."""
    graph = build_graph(manifest_path)
    return topo_order(graph)

if __name__ == "__main__":
    print("Dependency graph:", build_graph())
    print("Reload order:", get_reload_order())
