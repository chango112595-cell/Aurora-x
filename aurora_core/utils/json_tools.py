"""
Aurora JSON Tools - Universal JSON utilities
Eliminates dependency on external tools like jq
Works on any Python 3 environment without root access
"""

import json
import os
from typing import Any


def pretty_print_json(path: str) -> None:
    """Print formatted JSON file to stdout."""
    data = load_json(path)
    if data is not None:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(f"[Aurora JSON Tools] Could not load {path}")


def load_json(path: str) -> dict[str, Any] | None:
    """Load a JSON file."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Aurora JSON Tools] load_json error for {path}: {e}")
        return None


def save_json(path: str, data: dict[str, Any]) -> bool:
    """Save a JSON file."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        return True
    except Exception as e:
        print(f"[Aurora JSON Tools] save_json error for {path}: {e}")
        return False


def merge_json(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dicts."""
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = merge_json(base[k], v)
        else:
            base[k] = v
    return base


def query_json(data: dict[str, Any], path: str) -> Any:
    """Query nested keys using dot notation."""
    keys = path.split(".")
    cur = data
    for key in keys:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return None
    return cur


def validate_json(path: str) -> bool:
    """Return True if file is valid JSON."""
    try:
        with open(path, encoding="utf-8") as f:
            json.load(f)
        return True
    except Exception:
        return False


def json_to_string(data: Any) -> str:
    """Convert data to formatted JSON string."""
    return json.dumps(data, indent=2, sort_keys=True)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 json_tools.py <path_to_json>")
        sys.exit(1)
    pretty_print_json(sys.argv[1])
