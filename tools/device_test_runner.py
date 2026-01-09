#!/usr/bin/env python3
"""
Aurora Device Full-Universal Hybrid Test Runner

Behavior:
 - Auto-detects one connected embedded device (ESP32 / RP2040 / Cortex-M) if any (best-effort).
 - Always runs Linux SBC and Virtual Device tests.
 - Builds sample firmware for all profiles (simple artifacts).
 - Packages firmware into .axf using aurora_fw.builder.packager
 - Stages flash jobs via aurora_fw.flasher.flasher.stage_flash_job (suggestion mode)
 - Optionally flashes immediately with --auto-approve (dangerous, default False)
 - Runs hot-swap demo for an aurora module (installs plugin tar into aurora_modules)
 - Logs every step to logs/device_test_run.log

Requirements:
 - Run from repo root (Aurora-x)
 - Python3 environment with PACK 6/7 modules available on PYTHONPATH
 - For actual flashing tools: esptool.py, openocd, dfu-util, fastboot, ssh for Linux SBC (optional)
 - This script does not perform automatic firmware flashing unless --auto-approve is set.

Usage:
  python3 tools/device_test_runner.py [--auto-approve] [--force-target TARGET] [--clean]
Targets: esp32, cortex-m, rp2040, linux-sbc, virtual

"""

import argparse
import json
import shutil
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "logs"
LOG.mkdir(exist_ok=True)
RUN_LOG = LOG / "device_test_run.log"


def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    s = f"[{ts}] {msg}"
    print(s)
    with open(RUN_LOG, "a") as fh:
        fh.write(s + "\n")


# try import packager / flasher / hotswap etc (from previous packs)
try:
    from aurora_fw.builder.packager import create_axf
    from aurora_fw.flasher.flasher import available_tools, flash_now, stage_flash_job
    from aurora_fw.registry.registry import register as fw_register
except Exception as e:
    log("WARNING: PACK6 modules not fully importable: " + str(e))
    create_axf = None
    stage_flash_job = None
    flash_now = None
    available_tools = lambda: {}
    fw_register = lambda *a, **k: None

# hotswap (PACK7)
try:
    from cog_kernel.hotswap_manager.manager import apply_module_tar
except Exception:
    apply_module_tar = None


# utility - safe write helper
def write_sample_file(path: Path, content: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


# Builders for sample firmware (very simple)
def build_sample_esp32(outdir: Path):
    # Create a fake .bin file (in real use you would call esp-idf build)
    outdir.mkdir(parents=True, exist_ok=True)
    binf = outdir / "firmware.bin"
    write_sample_file(binf, b"ESP32-DUMMY-BINARY\n")
    # metadata
    (outdir / "meta.txt").write_text("esp32 sample firmware")
    return outdir


def build_sample_cortex_m(outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    binf = outdir / "firmware.bin"
    write_sample_file(binf, b"CORTEX-M-DUMMY-BINARY\n")
    (outdir / "meta.txt").write_text("cortex-m sample firmware")
    return outdir


def build_sample_rp2040(outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    uf2 = outdir / "firmware.uf2"
    write_sample_file(uf2, b"RP2040-UF2-DUMMY\n")
    (outdir / "meta.txt").write_text("rp2040 sample firmware")
    return outdir


def build_sample_linux_sbc(outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    # create a small deployable tar with a service script
    (outdir / "install.sh").write_text("#!/bin/sh\necho 'Hello from Linux SBC firmware sample'\n")
    (outdir / "meta.txt").write_text("linux-sbc sample artifact")
    return outdir


def build_sample_virtual(outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "run_sim.sh").write_text("#!/bin/sh\necho 'Virtual device running'\n")
    (outdir / "meta.txt").write_text("virtual device sample")
    return outdir


# package builder wrapper
def package_axf(sample_dir: Path, name: str, version="0.0.1", arch="generic", sign=False):
    out_axf = ROOT / "build" / f"{name}-{arch}-{int(time.time())}.axf"
    out_axf.parent.mkdir(parents=True, exist_ok=True)
    if create_axf:
        log(f"Packaging {sample_dir} -> {out_axf}")
        create_axf(
            str(sample_dir),
            str(out_axf),
            {"name": name, "version": version, "target_arch": arch},
            gpg_sign=sign,
        )
    else:
        # fallback: tarball
        import tarfile

        with tarfile.open(out_axf, "w:gz") as tf:
            tf.add(sample_dir, arcname=".")
        log("Packaged with fallback tar to " + str(out_axf))
    # register
    try:
        fw_register(str(out_axf), channel="test", meta={"source": "device_test_runner"})
    except Exception:
        pass
    return out_axf


# stage flash job wrapper
def stage_job(axf_path: Path, target: dict, reason: str):
    if stage_flash_job:
        jobfile = stage_flash_job(str(axf_path), target, reason)
        log(f"Staged flash job: {jobfile}")
        return jobfile
    else:
        # fallback: create a suggestion json
        SUG = ROOT / "aurora_fw" / "flasher" / "suggestions"
        SUG.mkdir(parents=True, exist_ok=True)
        job = {
            "id": f"sim-{int(time.time() * 1000)}",
            "axf": str(axf_path),
            "target": target,
            "reason": reason,
            "ts": time.time(),
        }
        p = SUG / f"{job['id']}.json"
        p.write_text(json.dumps(job, indent=2))
        log(f"Simulated stage job: {p}")
        return str(p)


# attempt to flash immediately (requires explicit approval)
def do_flash(jobfile: str):
    if flash_now:
        log("Executing flash for job " + str(jobfile))
        try:
            res = flash_now(jobfile)
            log("Flash result: " + str(res))
            return res
        except Exception as e:
            log("Flash failed: " + str(e))
            return {"ok": False, "error": str(e)}
    else:
        log("flash_now not available; simulating flash execution")
        return {"ok": False, "error": "no flasher"}


# hot-swap wrapper (install a sample plugin tar)
def do_hotswap_demo():
    if apply_module_tar:
        # create a small plugin tarball from plugin_template (if exists)
        plugin_src = ROOT / "aurora_core" / "plugin_template"
        if not plugin_src.exists():
            # create a tiny plugin folder
            tmp = ROOT / "build" / "demo_plugin"
            tmp.mkdir(parents=True, exist_ok=True)
            (tmp / "module.json").write_text(
                '{"name":"demo-plugin","version":"0.1.0","entry":"run.py"}'
            )
            (tmp / "run.py").write_text('print("demo-plugin executed")\n')
            plugin_src = tmp
        tarfile = ROOT / "build" / "demo-plugin.tar.gz"
        import tarfile as _tf

        with _tf.open(tarfile, "w:gz") as tf:
            tf.add(str(plugin_src), arcname="demo-plugin")
        log("Applying module tar " + str(tarfile))
        res = apply_module_tar(str(tarfile), "demo-plugin")
        log("Hot-swap result: " + str(res))
        return res
    else:
        log("Hot-swap manager not available; skipping")
        return {"ok": False, "reason": "no_hotswap"}


# detection heuristics
def detect_device():
    # Best-effort detection: check for serial devices and tool presence
    # Priorities: ESP32 if esptool found and /dev/ttyUSB* or /dev/ttyACM* present
    import glob
    import shutil

    # device nodes
    devs = (
        glob.glob("/dev/ttyUSB*")
        + glob.glob("/dev/ttyACM*")
        + glob.glob("/dev/ttyS*")
        + glob.glob("/dev/serial/by-id/*")
    )
    esptool = shutil.which("esptool.py") or shutil.which("esptool")
    openocd = shutil.which("openocd")
    uf2 = None  # no CLI
    # check microcontrollers
    if esptool and any("USB" in d.upper() or "ACM" in d.upper() or "ttyUSB" in d for d in devs):
        return "esp32"
    if openocd and any("tty" in d for d in devs):
        return "cortex-m"
    # RP2040 often enumerates as USB mass storage (hard to detect); leave as fallback
    return None


# run steps for a single device profile
def run_profile(profile: str, auto_approve=False):
    build_map = {
        "esp32": (build_sample_esp32, "esp32"),
        "cortex-m": (build_sample_cortex_m, "cortex-m"),
        "rp2040": (build_sample_rp2040, "rp2040"),
        "linux-sbc": (build_sample_linux_sbc, "linux-sbc"),
        "virtual": (build_sample_virtual, "virtual"),
    }
    if profile not in build_map:
        log("Unknown profile: " + profile)
        return {"ok": False, "profile": profile}
    builder, arch = build_map[profile]
    sample_dir = ROOT / "build" / f"sample_{profile}"
    # clean
    if sample_dir.exists():
        shutil.rmtree(sample_dir)
    builder(sample_dir)
    name = f"sample-{profile}"
    axf = package_axf(sample_dir, name, version="0.1.0", arch=arch, sign=False)
    # create target descriptor
    target = {"type": profile, "desc": f"demo target {profile}"}
    job = stage_job(axf, target, reason=f"demo automatic stage for {profile}")
    flash_res = None
    if auto_approve:
        flash_res = do_flash(job)
    return {"ok": True, "profile": profile, "axf": str(axf), "job": job, "flash": flash_res}


def run_hybrid(auto_approve=False, force_target=None, clean=False):
    log(
        "Starting Hybrid universal test: auto_approve=%s force=%s"
        % (auto_approve, str(force_target))
    )
    summary = {}
    if clean:
        log("Cleaning build and suggestions directories")
        shutil.rmtree(ROOT / "build", ignore_errors=True)
        shutil.rmtree(ROOT / "aurora_fw" / "flasher" / "suggestions", ignore_errors=True)
        Path(ROOT / "build").mkdir(exist_ok=True)

    # always run linux-sbc and virtual
    for p in ["linux-sbc", "virtual"]:
        res = run_profile(p, auto_approve=auto_approve)
        summary[p] = res

    # detect one embedded device unless forced
    target = force_target or detect_device()
    if target is None:
        log("No embedded device auto-detected. Skipping embedded flash in default hybrid run.")
        summary["embedded"] = {"ok": False, "reason": "no_device_detected"}
    else:
        log("Auto-detected embedded device: " + target)
        res = run_profile(target, auto_approve=auto_approve)
        summary[target] = res

    # run hot-swap demo (module install)
    hs = do_hotswap_demo()
    summary["hotswap"] = hs

    # final summary log
    log("Hybrid run finished. Summary:")
    log(json.dumps(summary, indent=2))
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--auto-approve", action="store_true", help="Auto-approve flashing (dangerous)")
    p.add_argument(
        "--force-target",
        choices=["esp32", "cortex-m", "rp2040"],
        help="Force the embedded target to test",
    )
    p.add_argument(
        "--clean", action="store_true", help="Clean build and suggestion dirs before run"
    )
    args = p.parse_args()
    try:
        run_hybrid(auto_approve=args.auto_approve, force_target=args.force_target, clean=args.clean)
    except Exception as e:
        log("ERROR: " + str(e))
        raise


if __name__ == "__main__":
    main()
