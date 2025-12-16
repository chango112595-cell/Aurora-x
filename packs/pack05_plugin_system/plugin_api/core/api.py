"""
Plugin API - defines the Plugin manifest schema and helper utilities.
Manifests must be JSON or YAML shaped like:
{
  "id": "publisher.plugin_name",
  "name": "Human Name",
  "version": "1.0.0",
  "entrypoint": "main.py",
  "description": "...",
  "permissions": ["network","gpu","io"]
}
"""

from pathlib import Path
import json

def validate_manifest(d: dict):
    required = ["id","name","version","entrypoint"]
    for k in required:
        if k not in d:
            raise ValueError(f"manifest missing {k}")
    if not isinstance(d["id"], str) or "." not in d["id"]:
        raise ValueError("id must be namespaced like publisher.plugin")
    return True

def load_manifest(path: Path):
    txt = path.read_text()
    if path.suffix.lower() in (".yaml",".yml"):
        try:
            import yaml
            return yaml.safe_load(txt)
        except Exception:
            pass
    return json.loads(txt)
