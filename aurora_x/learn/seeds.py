#!/usr/bin/env python3
"""
Persistent Learning Seeds for Aurora-X
Implements EMA-based seed bias learning with drift caps
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any


class SeedStore:
    """
    Manages persistent seed biases for function synthesis.
    Uses Exponential Moving Average (EMA) for bias updates with drift caps.
    """

    def __init__(
        self,
        path: str = ".aurora/seeds.json",
        alpha: float = 0.2,
        drift_cap: float = 0.15,
        top_n: int = 10
    ):
        """
        Initialize SeedStore with configurable parameters.

        Args:
            path: Path to persistent JSON file
            alpha: EMA smoothing factor (0-1, higher = more recent weight)
            drift_cap: Maximum allowed drift per update (±drift_cap)
            top_n: Number of top bias terms to keep
        """
        self.path = Path(path)
        self.alpha = alpha
        self.drift_cap = drift_cap
        self.top_n = top_n

        # Internal state
        self.biases: dict[str, float] = {}
        self.metadata: dict[str, Any] = {
            "created": None,
            "updated": None,
            "total_updates": 0,
            "config": {
                "alpha": alpha,
                "drift_cap": drift_cap,
                "top_n": top_n
            }
        }

        # Load existing data if available
        self.load()

    def load(self) -> None:
        """Load seed biases from persistent storage."""
        if self.path.exists():
            try:
                with open(self.path) as f:
                    data = json.load(f)
                    self.biases = data.get("biases", {})
                    self.metadata = data.get("metadata", self.metadata)
                    # Update config if changed
                    self.metadata["config"]["alpha"] = self.alpha
                    self.metadata["config"]["drift_cap"] = self.drift_cap
                    self.metadata["config"]["top_n"] = self.top_n
            except (json.JSONDecodeError, KeyError) as e:
                print(f"[SeedStore] Warning: Could not load {self.path}: {e}")
                self.biases = {}
        else:
            # First time creation
            self.metadata["created"] = time.time()
            self.save()

    def save(self) -> None:
        """Persist seed biases to storage."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Keep only top N biases
        sorted_biases = sorted(
            self.biases.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:self.top_n]
        self.biases = dict(sorted_biases)

        # Update metadata
        self.metadata["updated"] = time.time()

        data = {
            "biases": self.biases,
            "metadata": self.metadata
        }

        with open(self.path, 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True)

    def get_bias(self, seed_key: str) -> float:
        """
        Get bias for a specific seed.

        Args:
            seed_key: Unique identifier for the seed

        Returns:
            Bias value (0.0 if not found)
        """
        return self.biases.get(seed_key, 0.0)

    def get_biases(self) -> dict[str, float]:
        """Get all current biases."""
        return self.biases.copy()

    def update(self, result: dict[str, Any]) -> None:
        """
        Update seed bias based on synthesis result.
        Uses EMA with drift cap to prevent extreme changes.

        Args:
            result: Synthesis result containing:
                - seed_key: Unique identifier
                - score: Performance score (0-1)
                - success: Boolean success indicator
        """
        seed_key = result.get("seed_key")
        if not seed_key:
            return

        # Calculate new bias based on score and success
        score = result.get("score", 0.5)
        success = result.get("success", False)

        # Bias calculation: positive for good performance, negative for poor
        # Success adds bonus, failure adds penalty
        new_value = score - 0.5  # Center around 0
        if success:
            new_value += 0.1
        else:
            new_value -= 0.1

        # Get current bias
        current_bias = self.biases.get(seed_key, 0.0)

        # Apply EMA
        updated_bias = (1 - self.alpha) * current_bias + self.alpha * new_value

        # Apply drift cap
        drift = updated_bias - current_bias
        if abs(drift) > self.drift_cap:
            drift = self.drift_cap if drift > 0 else -self.drift_cap
            updated_bias = current_bias + drift

        # Clamp to reasonable range
        updated_bias = max(-1.0, min(1.0, updated_bias))

        # Store updated bias
        self.biases[seed_key] = updated_bias
        self.metadata["total_updates"] += 1

    def make_seed_key(self, func_signature: str, context: str = "") -> str:
        """
        Create a unique seed key from function signature and context.

        Args:
            func_signature: Function signature
            context: Additional context (e.g., spec description)

        Returns:
            Hashed seed key
        """
        combined = f"{func_signature}:{context}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def get_top_biases(self, n: int | None = None) -> list[tuple[str, float]]:
        """
        Get top N biases by absolute value.

        Args:
            n: Number of top biases (defaults to self.top_n)

        Returns:
            List of (seed_key, bias) tuples
        """
        n = n or self.top_n
        return sorted(
            self.biases.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:n]

    def get_summary(self) -> dict[str, Any]:
        """
        Get summary statistics about seed biases.

        Returns:
            Dictionary with summary stats
        """
        if not self.biases:
            return {
                "total_seeds": 0,
                "avg_bias": 0.0,
                "max_bias": 0.0,
                "min_bias": 0.0,
                "total_updates": self.metadata.get("total_updates", 0),
                "config": self.metadata.get("config", {})
            }

        bias_values = list(self.biases.values())
        return {
            "total_seeds": len(self.biases),
            "avg_bias": sum(bias_values) / len(bias_values),
            "max_bias": max(bias_values),
            "min_bias": min(bias_values),
            "total_updates": self.metadata.get("total_updates", 0),
            "config": self.metadata.get("config", {}),
            "top_biases": self.get_top_biases(5)  # Top 5 for summary
        }

    def reset(self) -> None:
        """Reset all biases (for testing or fresh start)."""
        self.biases = {}
        self.metadata["total_updates"] = 0
        self.save()


# Global singleton instance
_seed_store: SeedStore | None = None


def get_seed_store(
    path: str | None = None,
    alpha: float = 0.2,
    drift_cap: float = 0.15,
    top_n: int = 10
) -> SeedStore:
    """
    Get or create the global SeedStore instance.

    Args:
        path: Override default path (uses env var AURORA_SEEDS_PATH if set)
        alpha: EMA smoothing factor
        drift_cap: Maximum drift per update
        top_n: Number of top biases to keep

    Returns:
        SeedStore instance
    """
    global _seed_store

    if _seed_store is None:
        # Check environment for custom path
        if path is None:
            path = os.environ.get("AURORA_SEEDS_PATH", ".aurora/seeds.json")

        _seed_store = SeedStore(
            path=path or ".aurora/seeds.json",
            alpha=alpha,
            drift_cap=drift_cap,
            top_n=top_n
        )

    return _seed_store
