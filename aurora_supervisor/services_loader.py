"""
Aurora-X Services Loader
Activates controllers, hyperspeed, tools, and edge services.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "aurora_supervisor" / "data"
SERVICE_STATUS_FILE = DATA_DIR / "service_status.json"

CONTROLLERS = [
    ("Master Controller", "controllers/aurora_master_controller.py"),
    ("Nexus V3 Universal", "controllers/aurora_nexus_v3_universal.py"),
    ("Self-Healing System", "controllers/aurora_ultimate_self_healing_system.py"),
]

HYPERSPEED = [
    ("Hyperspeed Mode", "hyperspeed/aurora_hyper_speed_mode.py"),
]

EDGE_SERVICES = [
    ("Automotive UDS", "automotive/uds_service.py"),
    ("ESP32 OTA Server", "iot/esp32/ota_server.py"),
]

TOOLS = [
    ("Health Dashboard", "tools/aurora_health_dashboard.py"),
    ("Self Monitor", "tools/aurora_self_monitor.py"),
    ("Knowledge Engine", "tools/aurora_knowledge_engine.py"),
    ("Learning Engine", "tools/aurora_learning_engine.py"),
    ("Monitor Daemon", "tools/monitor_daemon.py"),
]

BACKEND_SERVICES = [
    ("Aurora Backend", "aurora_backend/main.py"),
    ("Aurora Hybrid System", "aurora_hybrid_system/main.py"),
    ("Aurora X Core", "aurora_x/main.py"),
]


class ServicesLoader:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.status = self._load_status()
        self.processes = {}

    def _load_status(self):
        if SERVICE_STATUS_FILE.exists():
            try:
                return json.loads(SERVICE_STATUS_FILE.read_text())
            except:
                pass
        return {}

    def _save_status(self):
        SERVICE_STATUS_FILE.write_text(json.dumps(self.status, indent=2))

    def log(self, msg, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        prefix = {"INFO": "[SVC]", "OK": "[OK]", "WARN": "[WARN]", "ERR": "[ERR]", "SKIP": "[SKIP]"}
        print(f"{timestamp} {prefix.get(level, '[SVC]')} {msg}")

    def start_python_service(self, name, script_path, background=True):
        full_path = ROOT / script_path
        if not full_path.exists():
            self.log(f"{name}: {script_path} not found", "SKIP")
            return False

        try:
            log_file = DATA_DIR / f"{name.lower().replace(' ', '_')}.log"

            if background:
                with open(log_file, "w") as lf:
                    process = subprocess.Popen(
                        [sys.executable, str(full_path)],
                        cwd=str(ROOT),
                        stdout=lf,
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                    )
                    self.processes[name] = process
                    self.status[name] = {
                        "running": True,
                        "pid": process.pid,
                        "script": script_path,
                        "started_at": time.ctime(),
                    }
                    self.log(f"{name} started (PID: {process.pid})", "OK")
                    return True
            else:
                result = subprocess.run(
                    [sys.executable, str(full_path)],
                    cwd=str(ROOT),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                return result.returncode == 0
        except FileNotFoundError:
            self.log(f"{name}: Python interpreter not found", "ERR")
        except Exception as e:
            self.log(f"{name} start error: {e}", "ERR")
        return False

    def start_category(self, category_name, services):
        self.log(f"--- {category_name} ---")
        success = 0
        for name, script in services:
            if self.start_python_service(name, script):
                success += 1
            time.sleep(0.2)
        return success

    def start_all(self):
        self.log("=" * 60)
        self.log("AURORA-X SERVICES LOADER")
        self.log("=" * 60)

        total = 0

        total += self.start_category("Controllers", CONTROLLERS)
        total += self.start_category("Hyperspeed", HYPERSPEED)
        total += self.start_category("Edge Services", EDGE_SERVICES)
        total += self.start_category("Tools", TOOLS)
        total += self.start_category("Backend Services", BACKEND_SERVICES)

        self.log("=" * 60)
        self.log(f"SERVICES LOADED: {total} services started")
        self.log("=" * 60)

        self._save_status()
        return total

    def stop_all(self):
        self.log("Stopping all services...")
        for name, proc in self.processes.items():
            try:
                proc.terminate()
                proc.wait(timeout=5)
                self.status[name]["running"] = False
                self.log(f"{name} stopped", "OK")
            except:
                try:
                    proc.kill()
                except:
                    pass
        self._save_status()

    def get_status(self):
        running = sum(1 for s in self.status.values() if isinstance(s, dict) and s.get("running"))
        return {
            "services": self.status,
            "running_count": running,
            "total_registered": len(self.status),
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Aurora-X Services Loader")
    parser.add_argument("action", choices=["start", "stop", "status"], default="start", nargs="?")
    args = parser.parse_args()

    loader = ServicesLoader()

    if args.action == "start":
        loader.start_all()
    elif args.action == "stop":
        loader.stop_all()
    elif args.action == "status":
        status = loader.get_status()
        print(json.dumps(status, indent=2))

    return loader.get_status()


if __name__ == "__main__":
    main()
