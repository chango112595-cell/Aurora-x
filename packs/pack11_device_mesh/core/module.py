"""pack11_device_mesh core.module - production implementation."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
NODES_PATH = DATA / "nodes.json"
DATA.mkdir(parents=True, exist_ok=True)


@dataclass
class Node:
    node_id: str
    meta: Dict[str, Any]
    last_seen: float


def _load_nodes() -> List[Node]:
    if not NODES_PATH.exists():
        return []
    raw = json.loads(NODES_PATH.read_text())
    return [Node(**item) for item in raw]


def _save_nodes(nodes: List[Node]) -> None:
    NODES_PATH.write_text(json.dumps([asdict(node) for node in nodes], indent=2))


def info():
    return {"pack": "pack11_device_mesh", "version": "1.0.0", "ts": time.time()}


def health_check():
    try:
        heartbeat = DATA / "health.touch"
        heartbeat.write_text(str(time.time()))
        return True
    except Exception:
        return False


def initialize():
    """Initialize the pack module."""
    print("[pack11_device_mesh] Initializing...")
    DATA.mkdir(parents=True, exist_ok=True)
    if not NODES_PATH.exists():
        _save_nodes([])
    return True


def shutdown():
    """Gracefully shutdown the pack module."""
    print("[pack11_device_mesh] Shutting down...")
    return True


def register_node(node_id: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    nodes = _load_nodes()
    for node in nodes:
        if node.node_id == node_id:
            node.meta.update(meta or {})
            node.last_seen = time.time()
            _save_nodes(nodes)
            return asdict(node)
    node = Node(node_id=node_id, meta=meta or {}, last_seen=time.time())
    nodes.append(node)
    _save_nodes(nodes)
    return asdict(node)


def heartbeat(node_id: str) -> Optional[Dict[str, Any]]:
    nodes = _load_nodes()
    for node in nodes:
        if node.node_id == node_id:
            node.last_seen = time.time()
            _save_nodes(nodes)
            return asdict(node)
    return None


def list_nodes() -> List[Dict[str, Any]]:
    return [asdict(node) for node in _load_nodes()]


def prune_stale(max_age: float) -> List[Dict[str, Any]]:
    now = time.time()
    nodes = _load_nodes()
    fresh = [node for node in nodes if now - node.last_seen <= max_age]
    _save_nodes(fresh)
    return [asdict(node) for node in fresh]


def build_topology() -> Dict[str, Any]:
    nodes = _load_nodes()
    topology = {
        "node_count": len(nodes),
        "nodes": [node.node_id for node in nodes],
        "edges": [],
    }
    for idx, node in enumerate(nodes):
        if idx + 1 < len(nodes):
            topology["edges"].append({"from": node.node_id, "to": nodes[idx + 1].node_id})
    return topology


def execute(command: str, params: dict = None):
    """Execute a command within this pack."""
    params = params or {}
    if command == "register_node":
        return {"status": "ok", "node": register_node(params.get("node_id", "unknown"), params.get("meta")), "ts": time.time()}
    if command == "heartbeat":
        return {"status": "ok", "node": heartbeat(params.get("node_id", "")), "ts": time.time()}
    if command == "list_nodes":
        return {"status": "ok", "nodes": list_nodes(), "ts": time.time()}
    if command == "prune_stale":
        return {"status": "ok", "nodes": prune_stale(float(params.get("max_age", 300))), "ts": time.time()}
    if command == "topology":
        return {"status": "ok", "topology": build_topology(), "ts": time.time()}
    return {"status": "ok", "command": command, "params": params, "ts": time.time()}
