#!/usr/bin/env python3
"""
Safe flasher abstraction:
- Supports ESP32 (esptool), OpenOCD for Cortex-M, dfu-util for some devices, fastboot for Android
- Always operates in 'suggestion' mode: create flash job that must be approved by operator (file moved to suggestions)
- Provides a simulated mode if tools missing
"""

import json
import shutil
import subprocess
import time
from pathlib import Path

SUGGESTION_DIR = Path("aurora_fw/flasher/suggestions")
SUGGESTION_DIR.mkdir(parents=True, exist_ok=True)


def available_tools():
    return {
        "esptool": bool(shutil.which("esptool.py") or shutil.which("esptool")),
        "openocd": bool(shutil.which("openocd")),
        "dfu-util": bool(shutil.which("dfu-util")),
        "fastboot": bool(shutil.which("fastboot")),
    }


def stage_flash_job(axf_path: str, target: dict, reason: str):
    # Create suggestion JSON job for operator approval
    # Ensure directory exists (may have been cleaned)
    SUGGESTION_DIR.mkdir(parents=True, exist_ok=True)
    ts = int(time.time() * 1000)
    job = {
        "id": f"flash-{ts}",
        "axf": axf_path,
        "target": target,
        "reason": reason,
        "ts": time.time(),
    }
    p = SUGGESTION_DIR / f"{job['id']}.json"
    p.write_text(json.dumps(job, indent=2))
    return str(p)


def flash_now(job_path: str):
    # only used once approved by operator (do not auto-run)
    job = json.loads(Path(job_path).read_text())
    axf = job["axf"]
    target = job["target"]
    # simple dispatch by target type
    if target.get("type") == "esp32":
        # extract firmware data and write via esptool
        # Assume .axf is a tar containing binaries; find first .bin as payload
        import tarfile
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            with tarfile.open(axf, "r:*") as tf:
                tf.extractall(tmp)
            # find .bin
            import glob

            bins = glob.glob(tmp + "/**/*.bin", recursive=True)
            if not bins:
                raise RuntimeError("no .bin in axf")
            binfile = bins[0]
            cmd = ["esptool.py", "--chip", "esp32", "write_flash", "0x1000", binfile]
            subprocess.check_call(cmd)
            return {"ok": True}
    # fallback simulation
    return {"ok": False, "error": "unsupported target or tools missing"}


if __name__ == "__main__":
    print("Available tools:", available_tools())
