"""
Plugin loader - validation and staging only.
Does NOT execute plugins. Execution is done by Supervisor + Hypervisor (PACK 4 & 3).
"""
import shutil, tempfile, json
from pathlib import Path
from .api import validate_manifest, load_manifest
from .registry import PluginRegistry

ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = ROOT / "data" / "plugins" / "packages"
PLUGINS_DIR.mkdir(parents=True, exist_ok=True)

class PluginLoader:
    def __init__(self):
        self.registry = PluginRegistry()

    def stage_package(self, package_path: str):
        """
        package_path: path to a directory containing plugin files and manifest.json/yaml
        This function copies files into data/plugins/packages/<plugin_id>/<version>/...
        """
        p = Path(package_path)
        if not p.exists():
            raise FileNotFoundError(p)
        mfile = None
        for cand in ("manifest.json","manifest.yaml","manifest.yml"):
            if (p / cand).exists():
                mfile = p / cand
                break
        if not mfile:
            raise ValueError("no manifest found in package")
        manifest = load_manifest(mfile)
        validate_manifest(manifest)
        plugin_id = manifest["id"]
        version = manifest["version"]
        target = PLUGINS_DIR / plugin_id / version
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(p, target)
        files = [str(x.relative_to(target)) for x in target.rglob("*") if x.is_file()]
        self.registry.register(manifest, files)
        return {"ok": True, "id": plugin_id, "version": version}
