"""
Aurora-X PACK System Unified Loader
Activates all 15 PACK systems in the correct order with health checks.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = Path(__file__).resolve().parents[1]
PACKS_DIR = ROOT / "packs"
LIVE_DIR = ROOT / "live"
DATA_DIR = ROOT / "aurora_supervisor" / "data"
PACK_STATUS_FILE = DATA_DIR / "pack_status.json"

PACK_ORDER = [
    "pack01_pack01",
    "pack02_env_profiler",
    "pack03_os_edge",
    "pack04_launcher",
    "pack05_plugin_system",
    "pack06_firmware_system",
    "pack07_secure_signing",
    "pack08_conversational_engine",
    "pack09_compute_layer",
    "pack10_autonomy_engine",
    "pack11_device_mesh",
    "pack12_toolforge",
    "pack13_runtime_2",
    "pack14_hw_abstraction",
    "pack15_intel_fabric",
]

PACK_NAMES = {
    "pack01_pack01": "Core System",
    "pack02_env_profiler": "Environment Profiler",
    "pack03_os_edge": "OS Edge Runtimes",
    "pack04_launcher": "Application Launcher",
    "pack05_plugin_system": "Plugin System",
    "pack06_firmware_system": "Firmware Manager",
    "pack07_secure_signing": "Secure Signing",
    "pack08_conversational_engine": "Conversational Engine",
    "pack09_compute_layer": "Compute Layer",
    "pack10_autonomy_engine": "Autonomy Engine",
    "pack11_device_mesh": "Device Mesh",
    "pack12_toolforge": "Tool Forge",
    "pack13_runtime_2": "Runtime 2.0",
    "pack14_hw_abstraction": "Hardware Abstraction",
    "pack15_intel_fabric": "Intelligence Fabric",
}


class PackLoader:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        LIVE_DIR.mkdir(parents=True, exist_ok=True)
        self.status = self._load_status()
        self.processes = {}

    def _load_status(self):
        if PACK_STATUS_FILE.exists():
            try:
                return json.loads(PACK_STATUS_FILE.read_text())
            except:
                pass
        return {pack: {"installed": False, "running": False, "healthy": False} for pack in PACK_ORDER}

    def _save_status(self):
        PACK_STATUS_FILE.write_text(json.dumps(self.status, indent=2))

    def log(self, msg, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        prefix = {"INFO": "[PACK]", "OK": "[OK]", "WARN": "[WARN]", "ERR": "[ERR]"}
        print(f"{timestamp} {prefix.get(level, '[PACK]')} {msg}")

    def install_pack(self, pack_id):
        pack_dir = PACKS_DIR / pack_id
        if not pack_dir.exists():
            self.log(f"{pack_id} directory not found", "ERR")
            return False

        install_script = pack_dir / "install.sh"
        if install_script.exists():
            try:
                result = subprocess.run(
                    ["bash", str(install_script), "--install"],
                    cwd=str(pack_dir),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    self.status[pack_id]["installed"] = True
                    self.log(f"{PACK_NAMES.get(pack_id, pack_id)} installed", "OK")
                    return True
                else:
                    self.log(f"{pack_id} install failed: {result.stderr}", "ERR")
            except subprocess.TimeoutExpired:
                self.log(f"{pack_id} install timed out", "WARN")
            except Exception as e:
                self.log(f"{pack_id} install error: {e}", "ERR")
        else:
            self.status[pack_id]["installed"] = True
            self.log(f"{PACK_NAMES.get(pack_id, pack_id)} marked as installed (no install.sh)", "OK")
            return True
        return False

    def start_pack(self, pack_id):
        pack_dir = PACKS_DIR / pack_id
        start_script = pack_dir / "start.sh"
        
        if not start_script.exists():
            for subdir in pack_dir.iterdir():
                if subdir.is_dir():
                    sub_start = subdir / "start.sh"
                    if sub_start.exists():
                        start_script = sub_start
                        break

        if start_script.exists():
            try:
                log_file = DATA_DIR / f"{pack_id}.log"
                with open(log_file, "w") as lf:
                    process = subprocess.Popen(
                        ["bash", str(start_script)],
                        cwd=str(start_script.parent),
                        stdout=lf,
                        stderr=subprocess.STDOUT,
                        start_new_session=True
                    )
                    self.processes[pack_id] = process
                    self.status[pack_id]["running"] = True
                    self.log(f"{PACK_NAMES.get(pack_id, pack_id)} started (PID: {process.pid})", "OK")
                    return True
            except Exception as e:
                self.log(f"{pack_id} start error: {e}", "ERR")
        else:
            self.log(f"{pack_id} has no start.sh - skipping start", "WARN")
            self.status[pack_id]["running"] = True
            return True
        return False

    def health_check_pack(self, pack_id):
        pack_dir = PACKS_DIR / pack_id
        health_script = pack_dir / "health_check.sh"
        
        if health_script.exists():
            try:
                result = subprocess.run(
                    ["bash", str(health_script)],
                    cwd=str(pack_dir),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.status[pack_id]["healthy"] = True
                    return True
            except:
                pass
        else:
            self.status[pack_id]["healthy"] = True
            return True
        return False

    def activate_pack(self, pack_id):
        self.log(f"Activating {PACK_NAMES.get(pack_id, pack_id)}...")
        
        if not self.status[pack_id].get("installed"):
            if not self.install_pack(pack_id):
                return False
        
        if not self.start_pack(pack_id):
            return False
        
        time.sleep(0.5)
        self.health_check_pack(pack_id)
        self._save_status()
        return True

    def activate_all(self, parallel=False):
        self.log("=" * 60)
        self.log("AURORA-X PACK SYSTEM LOADER")
        self.log(f"Activating {len(PACK_ORDER)} PACK systems...")
        self.log("=" * 60)
        
        success_count = 0
        failed = []

        if parallel:
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(self.activate_pack, pack): pack for pack in PACK_ORDER}
                for future in as_completed(futures):
                    pack = futures[future]
                    try:
                        if future.result():
                            success_count += 1
                        else:
                            failed.append(pack)
                    except Exception as e:
                        failed.append(pack)
                        self.log(f"{pack} activation error: {e}", "ERR")
        else:
            for pack_id in PACK_ORDER:
                if self.activate_pack(pack_id):
                    success_count += 1
                else:
                    failed.append(pack_id)

        self.log("=" * 60)
        self.log(f"PACK ACTIVATION COMPLETE: {success_count}/{len(PACK_ORDER)} successful")
        if failed:
            self.log(f"Failed packs: {', '.join(failed)}", "WARN")
        self.log("=" * 60)
        
        self._save_status()
        return success_count, failed

    def stop_all(self):
        self.log("Stopping all PACK systems...")
        for pack_id, proc in self.processes.items():
            try:
                proc.terminate()
                proc.wait(timeout=5)
                self.status[pack_id]["running"] = False
                self.log(f"{pack_id} stopped", "OK")
            except:
                proc.kill()
        self._save_status()

    def get_status(self):
        return {
            "packs": self.status,
            "running_count": sum(1 for s in self.status.values() if s.get("running")),
            "healthy_count": sum(1 for s in self.status.values() if s.get("healthy")),
            "total": len(PACK_ORDER)
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Aurora-X PACK System Loader")
    parser.add_argument("action", choices=["start", "stop", "status", "install"], default="start", nargs="?")
    parser.add_argument("--parallel", action="store_true", help="Activate packs in parallel")
    parser.add_argument("--pack", help="Specific pack to activate")
    args = parser.parse_args()

    loader = PackLoader()

    if args.action == "start":
        if args.pack:
            loader.activate_pack(args.pack)
        else:
            loader.activate_all(parallel=args.parallel)
    elif args.action == "stop":
        loader.stop_all()
    elif args.action == "status":
        status = loader.get_status()
        print(json.dumps(status, indent=2))
    elif args.action == "install":
        for pack in PACK_ORDER:
            loader.install_pack(pack)

    return loader.get_status()


if __name__ == "__main__":
    main()
