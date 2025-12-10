"""
Aurora JSON Tools - Universal JSON utilities
Eliminates dependency on external tools like jq
Works on any Python 3 environment without root access
"""
import json
from pathlib import Path
from typing import Any, Optional, Union


def pretty_print_json(path: Union[str, Path], indent: int = 2) -> None:
    """Pretty print a JSON file to stdout"""
    path = Path(path)
    try:
        with open(path) as f:
            data = json.load(f)
        print(json.dumps(data, indent=indent))
    except FileNotFoundError:
        print(f"[Aurora JSON Tool] File not found: {path}")
    except json.JSONDecodeError as e:
        print(f"[Aurora JSON Tool] Invalid JSON in {path}: {e}")
    except Exception as e:
        print(f"[Aurora JSON Tool] Could not parse {path}: {e}")


def load_json(path: Union[str, Path]) -> Optional[Any]:
    """Load JSON from file, returns None on error"""
    path = Path(path)
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"[Aurora JSON Tool] Load error {path}: {e}")
        return None


def save_json(path: Union[str, Path], data: Any, indent: int = 2) -> bool:
    """Save data to JSON file, returns success status"""
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        print(f"[Aurora JSON Tool] Save error {path}: {e}")
        return False


def merge_json(base_path: Union[str, Path], overlay_path: Union[str, Path], 
               output_path: Optional[Union[str, Path]] = None) -> Optional[dict]:
    """Merge two JSON files (overlay updates base)"""
    base = load_json(base_path)
    overlay = load_json(overlay_path)
    
    if base is None or overlay is None:
        return None
    
    if isinstance(base, dict) and isinstance(overlay, dict):
        result = {**base, **overlay}
        if output_path:
            save_json(output_path, result)
        return result
    
    print("[Aurora JSON Tool] Both files must contain JSON objects for merge")
    return None


def query_json(path: Union[str, Path], key_path: str, default: Any = None) -> Any:
    """Query a nested value using dot notation (e.g., 'config.database.host')"""
    data = load_json(path)
    if data is None:
        return default
    
    keys = key_path.split(".")
    current = data
    
    try:
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                current = current[int(key)]
            else:
                return default
        return current
    except (KeyError, IndexError, TypeError):
        return default


def validate_json(path: Union[str, Path]) -> bool:
    """Check if a file contains valid JSON"""
    path = Path(path)
    try:
        with open(path) as f:
            json.load(f)
        return True
    except:
        return False


def json_to_string(data: Any, indent: int = 2) -> str:
    """Convert data to pretty JSON string"""
    return json.dumps(data, indent=indent, default=str)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        pretty_print_json(sys.argv[1])
    else:
        print("Usage: python json_tools.py <json_file>")
