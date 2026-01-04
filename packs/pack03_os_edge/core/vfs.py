"""
Virtual filesystem abstraction for Aurora packs.

Design goals:
- Provide namespaced, per-pack virtual roots.
- Allow mounts (in-memory) and safe file ops.
- No use of FUSE; purely user-level virtual FS overlay.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class VirtualFS:
    def __init__(self, pack_id: str):
        self.pack_id = pack_id
        self.base = ROOT / "data" / "vfs" / pack_id
        self.base.mkdir(parents=True, exist_ok=True)

    def path(self, rel: str) -> Path:
        # sanitize rel
        safe = rel.lstrip("/").replace("..", "")
        return self.base / safe

    def write_text(self, rel: str, text: str, overwrite: bool = True):
        p = self.path(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists() and not overwrite:
            raise FileExistsError(p)
        p.write_text(text)
        return str(p)

    def read_text(self, rel: str) -> str:
        p = self.path(rel)
        if not p.exists():
            raise FileNotFoundError(p)
        return p.read_text()

    def listdir(self, rel: str = "."):
        p = self.path(rel)
        if not p.exists():
            return []
        return [str(x.name) for x in p.iterdir()]

    def remove(self, rel: str):
        p = self.path(rel)
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            return True
        return False
