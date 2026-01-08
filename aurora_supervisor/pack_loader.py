"""
Aurora-X PACK System Unified Loader
Activates all 15 PACK systems in the correct order with health checks.

Pack Module Locations:
- Main 15 PACK systems: packs/ directory (pack01_pack01 through pack15_intel_fabric)
- Generated modules: aurora_nexus_v3/generated_modules/ (~1,755 files)
- Core modules: aurora_nexus_v3/modules/ (~2,209 files)
- Manifest: aurora_nexus_v3/manifests/modules.manifest.json (550 registered modules)
"""

import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Main 15 PACK systems directory
PACKS_DIR = ROOT / "packs"

# Additional module directories (generated and core modules)
MODULES_DIRS = [
    ROOT / "aurora_nexus_v3" / "generated_modules",  # ~1,755 generated module files
    ROOT / "aurora_nexus_v3" / "modules",  # ~2,209 core module files
]

# Manifest file containing registered modules
MODULES_MANIFEST = ROOT / "aurora_nexus_v3" / "manifests" / "modules.manifest.json"

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
        self._module_cache = None

    def _scan_module_files(self):
        """Scan all module directories and count Python module files."""
        if self._module_cache is not None:
            return self._module_cache

        module_counts = {
            "generated_modules": 0,
            "core_modules": 0,
            "manifest_modules": 0,
            "total_files": 0,
            "by_category": {},
        }

        for modules_dir in MODULES_DIRS:
            if modules_dir.exists():
                for py_file in modules_dir.rglob("*.py"):
                    if py_file.name != "__init__.py":
                        module_counts["total_files"] += 1
                        if "generated_modules" in str(modules_dir):
                            module_counts["generated_modules"] += 1
                        else:
                            module_counts["core_modules"] += 1

                        # Count by category (analyzer, connector, etc.)
                        category = py_file.parent.name
                        if category not in ["generated_modules", "modules"]:
                            module_counts["by_category"][category] = (
                                module_counts["by_category"].get(category, 0) + 1
                            )

        # Load manifest count if available
        if MODULES_MANIFEST.exists():
            try:
                manifest_data = json.loads(MODULES_MANIFEST.read_text())
                module_counts["manifest_modules"] = len(manifest_data.get("modules", []))
            except Exception:
                pass

        self._module_cache = module_counts
        return module_counts

    def _load_status(self):
        if PACK_STATUS_FILE.exists():
            try:
                return json.loads(PACK_STATUS_FILE.read_text())
            except:
                pass
        return {
            pack: {"installed": False, "running": False, "healthy": False} for pack in PACK_ORDER
        }

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
                    timeout=30,
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
            self.log(
                f"{PACK_NAMES.get(pack_id, pack_id)} marked as installed (no install.sh)", "OK"
            )
            return True
        return False

    def start_pack(self, pack_id):
        pack_dir = PACKS_DIR / pack_id
        start_scripts = []

        main_start = pack_dir / "start.sh"
        if main_start.exists():
            start_scripts.append(main_start)

        for subdir in pack_dir.iterdir():
            if subdir.is_dir():
                sub_start = subdir / "start.sh"
                if sub_start.exists():
                    start_scripts.append(sub_start)

        if start_scripts:
            started = 0
            for start_script in start_scripts:
                try:
                    script_name = start_script.parent.name
                    log_file = DATA_DIR / f"{pack_id}_{script_name}.log"
                    with open(log_file, "w") as lf:
                        process = subprocess.Popen(
                            ["bash", str(start_script)],
                            cwd=str(start_script.parent),
                            stdout=lf,
                            stderr=subprocess.STDOUT,
                            start_new_session=True,
                        )
                        proc_key = f"{pack_id}_{script_name}"
                        self.processes[proc_key] = process
                        started += 1
                        if len(start_scripts) > 1:
                            self.log(
                                f"{PACK_NAMES.get(pack_id, pack_id)}/{script_name} started (PID: {process.pid})",
                                "OK",
                            )
                        else:
                            self.log(
                                f"{PACK_NAMES.get(pack_id, pack_id)} started (PID: {process.pid})",
                                "OK",
                            )
                except Exception as e:
                    self.log(f"{pack_id} start error: {e}", "ERR")

            if started > 0:
                self.status[pack_id]["running"] = True
                self.status[pack_id]["processes"] = started
                return True
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
                    timeout=10,
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
        module_counts = self._scan_module_files()
        self.log("=" * 60)
        self.log("AURORA-X PACK SYSTEM LOADER")
        self.log(f"Activating {len(PACK_ORDER)} PACK systems...")
        self.log(
            f"Total modules available: {module_counts['total_files']} "
            f"(generated: {module_counts['generated_modules']}, "
            f"core: {module_counts['core_modules']}, "
            f"manifest: {module_counts['manifest_modules']})"
        )
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
        self.log(f"PACK ACTIVATION COMPLETE: {success_count}/{len(PACK_ORDER)} packs successful")
        self.log(f"Total modules loaded: {module_counts['total_files']} module files")
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
        module_counts = self._scan_module_files()
        return {
            "packs": self.status,
            "running_count": sum(1 for s in self.status.values() if s.get("running")),
            "healthy_count": sum(1 for s in self.status.values() if s.get("healthy")),
            "total_packs": len(PACK_ORDER),
            "total_modules": module_counts["total_files"],
            "generated_modules": module_counts["generated_modules"],
            "core_modules": module_counts["core_modules"],
            "manifest_modules": module_counts["manifest_modules"],
            "modules_by_category": module_counts["by_category"],
            "total": len(PACK_ORDER),  # Kept for backwards compatibility
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Aurora-X PACK System Loader")
    parser.add_argument(
        "action", choices=["start", "stop", "status", "install"], default="start", nargs="?"
    )
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
