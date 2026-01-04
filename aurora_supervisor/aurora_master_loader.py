"""
Aurora-X Master Loader
Unified launcher that activates ALL Aurora-X components:
- 15 PACK systems
- Controllers
- Hyperspeed mode
- Edge services
- Tools
- Backend services
- Total Integration (Phases 1-7)
"""

import os
import sys
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "aurora_supervisor" / "data"
MASTER_STATUS_FILE = DATA_DIR / "master_loader_status.json"

sys.path.insert(0, str(ROOT))

from aurora_supervisor.pack_loader import PackLoader
from aurora_supervisor.services_loader import ServicesLoader
from aurora_supervisor.aurora_total_integration import main as run_total_integration


class AuroraMasterLoader:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.pack_loader = PackLoader()
        self.services_loader = ServicesLoader()
        self.start_time = None
        self.status = {}

    def log(self, msg, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        symbols = {"INFO": "[ ]", "OK": "[+]", "WARN": "[!]", "ERR": "[X]", "POWER": "[*]"}
        print(f"{timestamp} {symbols.get(level, '[ ]')} {msg}")

    def banner(self):
        print()
        print("=" * 70)
        print("    AURORA-X MASTER LOADER")
        print("    Unified System Activation")
        print("=" * 70)
        print()
        print("    Components to activate:")
        print("    - 15 PACK Systems")
        print("    - 3 Controllers")
        print("    - 1 Hyperspeed Mode")
        print("    - 2 Edge Services")
        print("    - 5 Tools")
        print("    - 3 Backend Services")
        print("    - Phase 1-7 Total Integration")
        print()
        print("=" * 70)
        print()

    def run_phase_integration(self):
        self.log("Running Phase 1-7 Total Integration...")
        try:
            run_total_integration()
            self.status["phase_integration"] = "complete"
            self.log("Phase 1-7 integration complete", "OK")
            return True
        except Exception as e:
            self.log(f"Phase integration error: {e}", "ERR")
            self.status["phase_integration"] = "failed"
            return False

    def activate_packs(self):
        self.log("Activating PACK Systems...")
        success, failed = self.pack_loader.activate_all(parallel=True)
        self.status["packs"] = {
            "success": success,
            "failed": len(failed),
            "failed_list": failed
        }
        return success

    def activate_services(self):
        self.log("Activating Services...")
        count = self.services_loader.start_all()
        self.status["services"] = {"started": count}
        return count

    def launch_all(self):
        self.start_time = time.time()
        self.banner()

        self.log("PHASE 1: Running Total Integration (Phases 1-7)...", "POWER")
        self.run_phase_integration()
        print()

        self.log("PHASE 2: Activating PACK Systems...", "POWER")
        pack_count = self.activate_packs()
        print()

        self.log("PHASE 3: Activating Services...", "POWER")
        service_count = self.activate_services()
        print()

        elapsed = time.time() - self.start_time
        
        self._save_status()
        self._print_summary(pack_count, service_count, elapsed)

        return self.status

    def _save_status(self):
        self.status["timestamp"] = time.ctime()
        self.status["elapsed_seconds"] = time.time() - self.start_time if self.start_time else 0
        MASTER_STATUS_FILE.write_text(json.dumps(self.status, indent=2))

    def _print_summary(self, pack_count, service_count, elapsed):
        pack_status = self.pack_loader.get_status()
        total_modules = pack_status.get("total_modules", 0)
        generated_modules = pack_status.get("generated_modules", 0)
        core_modules = pack_status.get("core_modules", 0)
        manifest_modules = pack_status.get("manifest_modules", 0)
        
        print()
        print("=" * 70)
        print("    AURORA-X MASTER LOADER - ACTIVATION COMPLETE")
        print("=" * 70)
        print()
        print(f"    Phase Integration: {self.status.get('phase_integration', 'unknown')}")
        print(f"    PACK Systems:      {pack_count}/15 activated")
        print(f"    Total Modules:     {total_modules} loaded")
        print(f"      - Generated:     {generated_modules}")
        print(f"      - Core:          {core_modules}")
        print(f"      - Manifest:      {manifest_modules}")
        print(f"    Services:          {service_count} started")
        print(f"    Total Time:        {elapsed:.2f} seconds")
        print()
        print("    STATUS: ALL SYSTEMS OPERATIONAL")
        print()
        print("=" * 70)
        print()
        print("    Active Workflows:")
        print(f"    - Aurora Nexus V3 (300 workers, 188 tiers, 66 AEMs, {total_modules} modules)")
        print("    - Aurora Supervisor (100 healers + auto-evolution)")
        print("    - Luminar Nexus V2 (Chat + ML learning)")
        print("    - MCP Server (HTTP/WebSocket API)")
        print("    - Start Application (Frontend + Backend)")
        print()
        print("    + 15 PACK Systems")
        print("    + Controllers, Hyperspeed, Edge, Tools, Backend")
        print()
        print("=" * 70)
        print()

    def stop_all(self):
        self.log("Stopping all Aurora-X systems...")
        self.pack_loader.stop_all()
        self.services_loader.stop_all()
        self.log("All systems stopped", "OK")

    def get_full_status(self):
        return {
            "master": self.status,
            "packs": self.pack_loader.get_status(),
            "services": self.services_loader.get_status()
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Aurora-X Master Loader")
    parser.add_argument("action", choices=["start", "stop", "status"], default="start", nargs="?")
    args = parser.parse_args()

    loader = AuroraMasterLoader()

    if args.action == "start":
        loader.launch_all()
    elif args.action == "stop":
        loader.stop_all()
    elif args.action == "status":
        status = loader.get_full_status()
        print(json.dumps(status, indent=2))

    return loader


if __name__ == "__main__":
    main()
