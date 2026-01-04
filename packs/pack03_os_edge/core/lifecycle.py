#!/usr/bin/env python3
"""
lifecycle.py - Manage module lifecycle for packs:
- load module contents into vfs
- activate (start) module processes
- hot-swap (replace module files and restart)
Uses Hypervisor and RuntimeLoader from earlier sections.
"""

import shutil
import time
from pathlib import Path

from .hypervisor import Hypervisor
from .runtime_loader import RuntimeLoader
from .vfs import VirtualFS

ROOT = Path(__file__).resolve().parents[2]


class ModuleLifecycle:
    def __init__(self, pack_id: str):
        self.pack_id = pack_id
        self.vfs = VirtualFS(pack_id)
        self.hv = Hypervisor()
        self.rl = RuntimeLoader(pack_id)

    def load_from_dir(self, src_dir: str, overwrite=True):
        src = Path(src_dir)
        if not src.exists():
            raise FileNotFoundError(src)
        # copy into pack vfs root (replace files)
        dest = self.vfs.path(".")
        for p in src.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(src))
                dest_p = dest / rel
                dest_p.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(p), str(dest_p))
        return True

    def activate(self, entrypoint_cmd: str, background=True):
        return self.hv.run_in(self.pack_id, entrypoint_cmd, background=background)

    def hotswap(self, src_dir: str, entrypoint_cmd: str):
        # create backup
        backup = ROOT / "backups" / self.pack_id / str(int(time.time()))
        backup.parent.mkdir(parents=True, exist_ok=True)
        if self.vfs.path(".").exists():
            shutil.copytree(str(self.vfs.path(".")), str(backup), dirs_exist_ok=True)
        # load new files
        self.load_from_dir(src_dir, overwrite=True)
        # restart
        res = self.activate(entrypoint_cmd, background=True)
        return res


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("pack")
    p.add_argument("--cmd", default="python3 hello.py")
    args = p.parse_args()
    m = ModuleLifecycle(args.pack)
    print(m.activate(args.cmd))
