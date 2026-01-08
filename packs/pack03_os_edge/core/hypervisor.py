"""
hypervisor.py - lightweight process-level sandbox orchestrator.

This is NOT a hardware hypervisor. It's a userland orchestrator that:
- creates per-pack sandboxes (using VFS paths)
- uses Popen to run processes inside a pack's workdir
- configures resource governor hints
- provides lifecycle hooks: start, stop, status, list
"""

from pathlib import Path

from .process_abstraction import PackProcess
from .resource_governor import ResourceGovernor
from .vfs import VirtualFS

ROOT = Path(__file__).resolve().parents[2]


class SandboxInstance:
    def __init__(self, pack_id: str, governor: ResourceGovernor | None = None):
        self.pack_id = pack_id
        self.vfs = VirtualFS(pack_id)
        self.process = PackProcess(pack_id, workdir=str(self.vfs.path(".")))
        self.gov = governor or ResourceGovernor(pack_id)

    def run(self, cmd: str, timeout: int | None = 30, background: bool = False):
        # apply resource limits (best effort)
        self.gov.apply_limits()
        if background:
            pid = self.process.run_background(cmd)
            return {"ok": True, "pid": pid}
        else:
            return self.process.run(cmd, timeout=timeout)


class Hypervisor:
    def __init__(self):
        self.instances: dict[str, SandboxInstance] = {}

    def create_instance(self, pack_id: str):
        if pack_id in self.instances:
            return self.instances[pack_id]
        inst = SandboxInstance(pack_id)
        self.instances[pack_id] = inst
        return inst

    def destroy_instance(self, pack_id: str):
        if pack_id in self.instances:
            # best-effort cleanup: remove vfs and data? we'll keep data for safety
            del self.instances[pack_id]
            return True
        return False

    def list_instances(self):
        return list(self.instances.keys())

    def run_in(self, pack_id: str, cmd: str, timeout: int | None = 30, background=False):
        inst = self.create_instance(pack_id)
        return inst.run(cmd, timeout=timeout, background=background)


# short CLI if run directly
if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser()
    p.add_argument("pack")
    p.add_argument("--cmd", required=True)
    p.add_argument("--bg", action="store_true")
    args = p.parse_args()
    hv = Hypervisor()
    res = hv.run_in(args.pack, args.cmd, background=args.bg)
    print(json.dumps(res))
