"""
Aurora Atomic I/O Utilities

Production-ready atomic file operations for snapshot persistence.
Prevents JSON corruption and provides graceful error recovery.
"""

import os
import json
from typing import Any, Dict, Optional, Union
from pathlib import Path


def atomic_json_write(path: Union[str, Path], data: Any) -> None:
    """
    Write JSON atomically to prevent corruption.
    
    Uses a temp file and atomic rename to ensure the file is never
    in a partially-written state.
    
    Args:
        path: File path to write to
        data: JSON-serializable data
    """
    path_str = str(path)
    tmp = f"{path_str}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path_str)


def load_snapshot(path: Union[str, Path], default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Load JSON with graceful recovery.
    
    If the file doesn't exist or is corrupted, returns the default value
    instead of raising an exception.
    
    Args:
        path: File path to read from
        default: Default value if file cannot be loaded
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        with open(str(path), encoding="utf-8") as f:
            result = json.load(f)
            if isinstance(result, dict):
                return result
            return default or {"status": "recovered", "events": []}
    except Exception:
        return default or {"status": "recovered", "events": []}
