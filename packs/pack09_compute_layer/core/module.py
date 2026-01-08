"""pack09_compute_layer core.module - production implementation."""

from __future__ import annotations

import statistics
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)


def info():
    return {"pack": "pack09_compute_layer", "version": "1.0.0", "ts": time.time()}


def health_check():
    try:
        heartbeat = DATA / "health.touch"
        heartbeat.write_text(str(time.time()))
        return True
    except Exception:
        return False


def initialize():
    """Initialize the pack module."""
    print("[pack09_compute_layer] Initializing...")
    DATA.mkdir(parents=True, exist_ok=True)
    return True


def shutdown():
    """Gracefully shutdown the pack module."""
    print("[pack09_compute_layer] Shutting down...")
    return True


def _ensure_numbers(values: list[Any]) -> list[float]:
    return [float(v) for v in values]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _execute_math(operation: str, values: list[Any]) -> dict[str, Any]:
    numbers = _ensure_numbers(values)
    if not numbers:
        return {"ok": False, "error": "no values provided"}
    if operation == "add":
        return {"ok": True, "result": sum(numbers)}
    if operation == "multiply":
        result = 1.0
        for value in numbers:
            result *= value
        return {"ok": True, "result": result}
    if operation == "subtract":
        result = numbers[0]
        for value in numbers[1:]:
            result -= value
        return {"ok": True, "result": result}
    if operation == "divide":
        result = numbers[0]
        for value in numbers[1:]:
            result /= value
        return {"ok": True, "result": result}
    if operation == "mean":
        return {"ok": True, "result": statistics.mean(numbers)}
    if operation == "median":
        return {"ok": True, "result": statistics.median(numbers)}
    if operation == "min":
        return {"ok": True, "result": min(numbers)}
    if operation == "max":
        return {"ok": True, "result": max(numbers)}
    return {"ok": False, "error": f"unsupported operation: {operation}"}


def execute(command: str, params: dict = None):
    """Execute a command within this pack."""
    params = params or {}
    if command == "compute":
        operation = params.get("operation", "add")
        values = params.get("values", [])
        result = _execute_math(operation, values)
        return {
            "status": "ok",
            "operation": operation,
            "values": values,
            "result": result,
            "ts": time.time(),
        }
    if command == "dot":
        a = _ensure_numbers(params.get("a", []))
        b = _ensure_numbers(params.get("b", []))
        return {"status": "ok", "result": _dot(a, b), "ts": time.time()}
    if command == "batch":
        tasks = params.get("tasks", [])
        results = []
        for task in tasks:
            results.append(_execute_math(task.get("operation", "add"), task.get("values", [])))
        return {"status": "ok", "results": results, "ts": time.time()}
    return {"status": "ok", "command": command, "params": params, "ts": time.time()}
