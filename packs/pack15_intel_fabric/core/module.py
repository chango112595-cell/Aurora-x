"""pack15_intel_fabric core.module - production implementation."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json
import statistics
import time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OBSERVATIONS_PATH = DATA / "observations.jsonl"
DATA.mkdir(parents=True, exist_ok=True)


def info():
    return {"pack": "pack15_intel_fabric", "version": "1.0.0", "ts": time.time()}


def health_check():
    try:
        heartbeat = DATA / "health.touch"
        heartbeat.write_text(str(time.time()))
        return True
    except Exception:
        return False


def initialize():
    """Initialize the pack module."""
    print("[pack15_intel_fabric] Initializing...")
    DATA.mkdir(parents=True, exist_ok=True)
    return True


def shutdown():
    """Gracefully shutdown the pack module."""
    print("[pack15_intel_fabric] Shutting down...")
    return True


def record_observation(category: str, value: float, tags: Dict[str, Any] | None = None) -> Dict[str, Any]:
    event = {"category": category, "value": value, "tags": tags or {}, "ts": time.time()}
    with OBSERVATIONS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
    return event


def load_observations(limit: int = 100) -> List[Dict[str, Any]]:
    if not OBSERVATIONS_PATH.exists():
        return []
    items: List[Dict[str, Any]] = []
    with OBSERVATIONS_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    return items[-limit:]


def aggregate(category: str) -> Dict[str, Any]:
    observations = [obs for obs in load_observations(500) if obs.get("category") == category]
    values = [float(obs.get("value", 0)) for obs in observations]
    if not values:
        return {"count": 0, "average": None, "stdev": None}
    return {
        "count": len(values),
        "average": statistics.mean(values),
        "stdev": statistics.pstdev(values),
    }


def detect_anomalies(category: str, threshold: float = 2.0) -> List[Dict[str, Any]]:
    observations = [obs for obs in load_observations(500) if obs.get("category") == category]
    values = [float(obs.get("value", 0)) for obs in observations]
    if len(values) < 2:
        return []
    mean = statistics.mean(values)
    stdev = statistics.pstdev(values) or 1.0
    anomalies = [obs for obs in observations if abs(float(obs.get("value", 0)) - mean) / stdev >= threshold]
    return anomalies


def execute(command: str, params: dict = None):
    """Execute a command within this pack."""
    params = params or {}
    if command == "record":
        event = record_observation(
            params.get("category", "signal"),
            float(params.get("value", 0.0)),
            params.get("tags", {}),
        )
        return {"status": "ok", "event": event, "ts": time.time()}
    if command == "aggregate":
        return {"status": "ok", "summary": aggregate(params.get("category", "signal")), "ts": time.time()}
    if command == "anomalies":
        return {
            "status": "ok",
            "anomalies": detect_anomalies(params.get("category", "signal"), float(params.get("threshold", 2.0))),
            "ts": time.time(),
        }
    return {"status": "ok", "command": command, "params": params, "ts": time.time()}
