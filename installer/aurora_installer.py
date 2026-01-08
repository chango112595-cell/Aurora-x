#!/usr/bin/env python3
"""
installer/aurora_installer.py - Universal Aurora Installer CORE (Python).
Hybrid manifest support (yaml/json), auto-detects best installer mode per device,
supports --dry-run, --install, --staging, --activate, --rollback, and operator approval gating.

Usage:
  python3 installer/aurora_installer.py --help
"""

import argparse
import json
import platform
import shutil
import subprocess
import time
from pathlib import Path

try:
    import yaml
except Exception:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
PACKS_DIR = ROOT / "packs"
STAGING_DIR = ROOT / "staging"
LIVE_DIR = ROOT / "live"
BACKUPS_DIR = ROOT / "backups"
AUDIT_DIR = ROOT / "audit"

for d in (STAGING_DIR, LIVE_DIR, BACKUPS_DIR, AUDIT_DIR):
    d.mkdir(parents=True, exist_ok=True)


def load_manifest(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text()
    if path.suffix.lower() in (".yaml", ".yml") and yaml:
        return yaml.safe_load(text)
    try:
        return json.loads(text)
    except Exception:
        if yaml:
            return yaml.safe_load(text)
        raise


def detect_environment():
    info = {
        "platform": platform.system().lower(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }
    try:
        with open("/proc/cpuinfo") as f:
            cpu = f.read().lower()
            if "raspberry pi" in cpu or "bcm" in cpu:
                info["device"] = "raspberrypi"
            elif "nvidia" in cpu:
                info["device"] = "jetson"
    except Exception:
        pass
    return info


def best_install_mode(env_info):
    if shutil.which("python3") or shutil.which("python"):
        return "python"
    if shutil.which("node"):
        return "node"
    if env_info.get("platform") == "windows":
        return "windows"
    return "generic"


def run_health_check(pack_live_path: Path, timeout: int = 30):
    hc = pack_live_path / "health_check.sh"
    if hc.exists():
        proc = subprocess.run(["bash", str(hc)], capture_output=True, text=True)
        ok = proc.returncode == 0
        out = proc.stdout + proc.stderr
        return ok, out
    return True, "no health_check present"


def stage_pack(pack_dir: Path):
    assert pack_dir.exists()
    name = pack_dir.name
    staging_target = STAGING_DIR / name
    if staging_target.exists():
        shutil.rmtree(staging_target)
    shutil.copytree(pack_dir, staging_target)
    return staging_target


def activate_pack(staging_target: Path):
    name = staging_target.name
    live_target = LIVE_DIR / name
    timestamp = str(int(time.time()))
    backup_target = BACKUPS_DIR / name / timestamp
    if live_target.exists():
        backup_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(live_target), str(backup_target))
    shutil.move(str(staging_target), str(live_target))
    return live_target, backup_target


def deploy_pack(pack_id: str, dry_run=True, auto_approve=False):
    pack_path = PACKS_DIR / pack_id
    if not pack_path.exists():
        raise FileNotFoundError(f"pack not found: {pack_path}")
    print(f"[installer] Staging {pack_id} -> staging")
    staged = stage_pack(pack_path)
    print("[installer] Running pre-activation tests (dry-run)")
    install_sh = staged / "install.sh"
    if install_sh.exists():
        p = subprocess.run(["bash", str(install_sh), "--dry-run"], capture_output=True, text=True)
        print("[installer] install.sh output:", p.stdout, p.stderr)
        if p.returncode != 0:
            print("[installer] Preinstall tests failed; aborting")
            return False
    if dry_run:
        print("[installer] Dry run complete. To activate run with --install")
        return True
    if not auto_approve:
        ans = input("Operator approval required. Type APPROVE to continue: ")
        if ans.strip().upper() != "APPROVE":
            print("Operator approval not granted. Aborting.")
            return False
    live, backup = activate_pack(staged)
    print(f"[installer] Activated {pack_id} -> {live} (backup: {backup})")
    ok, out = run_health_check(live, timeout=30)
    if not ok:
        print("[installer] Health-check failed. Rolling back.")
        if backup.exists():
            if live.exists():
                shutil.rmtree(live)
            shutil.move(str(backup), str(live))
            print("[installer] Rolled back to backup", backup)
        return False
    print("[installer] Health-check OK.")
    return True


def rollback_pack(pack_id: str, ts="latest"):
    pack_backups = BACKUPS_DIR / pack_id
    if not pack_backups.exists():
        print("No backups for pack", pack_id)
        return False
    if ts == "latest":
        choices = sorted([d.name for d in pack_backups.iterdir() if d.is_dir()], reverse=True)
        if not choices:
            print("No valid backups")
            return False
        ts = choices[0]
    backup = pack_backups / ts
    live_target = LIVE_DIR / pack_id
    if live_target.exists():
        shutil.rmtree(live_target)
    shutil.move(str(backup), str(live_target))
    print("Rollback successful for", pack_id)
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "action", choices=["stage", "install", "activate", "rollback", "dry-run", "info"]
    )
    p.add_argument("--pack", required=False, help="pack id e.g. pack01_unified_process")
    p.add_argument("--auto-approve", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    env = detect_environment()
    print("[installer] env:", env)
    mode = best_install_mode(env)
    print("[installer] preferred installer mode:", mode)
    if args.action in ("stage", "dry-run"):
        if not args.pack:
            p.error("--pack required")
        print("Staging/dry-run:", args.pack)
        deploy_pack(args.pack, dry_run=True, auto_approve=args.auto_approve)
    elif args.action in ("install", "activate"):
        if not args.pack:
            p.error("--pack required")
        ok = deploy_pack(args.pack, dry_run=False, auto_approve=args.auto_approve)
        print("install result:", ok)
    elif args.action == "rollback":
        if not args.pack:
            p.error("--pack required")
        rollback_pack(args.pack)
    elif args.action == "info":
        print("Packs available:", [p.name for p in PACKS_DIR.iterdir() if p.is_dir()])


if __name__ == "__main__":
    main()
