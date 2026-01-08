#!/usr/bin/env python3
"""
Hot-swap orchestration:
- Accepts new module package (tar .py files)
- Runs evaluator (tests) in isolated sandbox (Docker or subprocess)
- If pass, schedules swap with graceful draining (notify agents, pause traffic)
"""

import shutil
import tarfile
import tempfile
import time
from pathlib import Path

from ..core.evaluator import run_tests_for_module
from ..core.hotswap import HotSwapManager

HSM = HotSwapManager()


def apply_module_tar(tar_path: str, module_name: str):
    # extract to temp, run tests, then move into place if ok
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(tar_path, "r:*") as tf:
            tf.extractall(tmp)
        # run tests
        res = run_tests_for_module(tmp)
        if res.get("rc", 0) != 0:
            return {"ok": False, "test": res}
        # move into aurora_modules/<module_name>
        dest = Path("aurora_modules") / module_name
        if dest.exists():
            backup = Path(".aurora_backup") / f"{module_name}-{int(time.time())}"
            shutil.move(str(dest), str(backup))
        shutil.copytree(tmp, dest)
        # attempt hot reload
        HSM.reload(f"aurora_modules.{module_name}")
        return {"ok": True, "installed": str(dest)}
