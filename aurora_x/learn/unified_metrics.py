"""
Unified learning metrics for Aurora.
Combines corpus learning + performance tracking.
"""

import json
import time
from pathlib import Path
from typing import Any


class UnifiedLearningTracker:
    """Unified learning across all Aurora systems."""

    def __init__(self):
        """
              Init  
            
            Args:
            """
        self.metrics_file = Path(".aurora_knowledge/unified_metrics.json")
        self.metrics_file.parent.mkdir(exist_ok=True)

    def record_execution(self, system: str, task: str, method: str, duration_ms: float, success: bool, **metadata):
        """Record an execution for learning."""
        metrics = self.load_metrics()

        execution = {
            "timestamp": time.time(),
            "system": system,
            "task": task,
            "method": method,
            "duration_ms": duration_ms,
            "success": success,
            **metadata,
        }

        metrics["executions"].append(execution)

        # Update aggregates
        key = f"{system}::{method}"
        if key not in metrics["aggregates"]:
            metrics["aggregates"][key] = {"count": 0, "success_count": 0, "total_duration": 0, "avg_duration": 0}

        agg = metrics["aggregates"][key]
        agg["count"] += 1
        if success:
            agg["success_count"] += 1
        agg["total_duration"] += duration_ms
        agg["avg_duration"] = agg["total_duration"] / agg["count"]

        self.save_metrics(metrics)

    def load_metrics(self) -> dict[str, Any]:
        """Load metrics."""
        if self.metrics_file.exists():
            return json.loads(self.metrics_file.read_text())
        return {"executions": [], "aggregates": {}, "speed_records": {}}

    def save_metrics(self, metrics: dict[str, Any]):
        """Save metrics."""
        self.metrics_file.write_text(json.dumps(metrics, indent=2))

    def get_best_method(self, system: str = None) -> str:
        """Get best performing method."""
        metrics = self.load_metrics()

        best_method = None
        best_score = 0

        for key, agg in metrics["aggregates"].items():
            if system and not key.startswith(f"{system}::"):
                continue

            if agg["count"] == 0:
                continue

            success_rate = agg["success_count"] / agg["count"]
            speed_score = 1000 / max(1, agg["avg_duration"])
            score = success_rate * speed_score

            if score > best_score:
                best_score = score
                best_method = key.split("::")[-1]

        return best_method or "unknown"

    def get_stats(self) -> dict[str, Any]:
        """Get overall statistics."""
        metrics = self.load_metrics()

        total_executions = len(metrics["executions"])
        total_success = sum(1 for e in metrics["executions"] if e["success"])

        return {
            "total_executions": total_executions,
            "total_success": total_success,
            "success_rate": f"{(total_success / max(1, total_executions) * 100):.1f}%",
            "methods": len(metrics["aggregates"]),
            "aggregates": metrics["aggregates"],
        }


# Global instance
_tracker = UnifiedLearningTracker()


def record(system: str, task: str, method: str, duration_ms: float, success: bool, **metadata):
    """Record an execution."""
    _tracker.record_execution(system, task, method, duration_ms, success, **metadata)


def get_best_method(system: str = None) -> str:
    """Get best performing method."""
    return _tracker.get_best_method(system)


def get_stats() -> dict[str, Any]:
    """Get statistics."""
    return _tracker.get_stats()


__all__ = ["record", "get_best_method", "get_stats", "UnifiedLearningTracker"]
