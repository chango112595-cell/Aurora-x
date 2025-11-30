#!/usr/bin/env python3
"""
launcher.py - Unified launcher that reads a launch manifest (pack-specific) and
starts modules under the supervision system. Provides CLI to list/start/stop.
Uses a shared Supervisor instance for unified control.
"""
import argparse, json, time, os
from pathlib import Path
from .supervisor import Supervisor
from .orchestrator import Orchestrator
from .log_unifier import LogUnifier

ROOT = Path(__file__).resolve().parents[1]
LAUNCH_MANIFEST = ROOT / "data" / "launch_manifest.json"

class LauncherCLI:
    def __init__(self, manifest_path=None):
        self._sup = Supervisor()
        self._orch = Orchestrator(manifest_path, supervisor=self._sup)
        self.log = LogUnifier(ROOT / "logs" / "launcher.log")

    @property
    def sup(self):
        return self._sup

    @property
    def orch(self):
        return self._orch

    def list(self):
        return self.orch.list_jobs()

    def start(self, name):
        result = self.orch.start_job(name)
        self.log.append("launcher", f"started job {name}: rc={result.get('rc', 'N/A')}")
        return result

    def stop(self, name):
        result = self.sup.stop_job(name)
        self.log.append("launcher", f"stopped job {name}")
        return result

    def start_all(self):
        results = self.orch.start_all()
        for name, res in results.items():
            self.log.append("launcher", f"started job {name}: rc={res.get('rc', 'N/A')}")
        return results

    def stop_all(self):
        return self.sup.stop_all()

    def shutdown(self):
        """Shutdown the supervisor and stop all jobs."""
        self.sup.stop_all()
        self.sup.stop()
        Supervisor.reset_instance()

def load_manifest(path=None):
    manifest_path = Path(path) if path else LAUNCH_MANIFEST
    if manifest_path.exists():
        return json.loads(manifest_path.read_text())
    return {"jobs": []}

def main():
    p = argparse.ArgumentParser(description="Pack04 Unified Launcher")
    p.add_argument("cmd", choices=["list", "start", "stop", "run"], help="Command to execute")
    p.add_argument("--job", required=False, help="Job name for start/stop")
    p.add_argument("--manifest", required=False, help="Path to launch manifest")
    args = p.parse_args()

    launcher = LauncherCLI(args.manifest)

    try:
        if args.cmd == "list":
            print(json.dumps(launcher.list(), indent=2))
        elif args.cmd == "start" and args.job:
            print(json.dumps(launcher.start(args.job), indent=2))
        elif args.cmd == "stop" and args.job:
            print(json.dumps(launcher.stop(args.job), indent=2))
        elif args.cmd == "run":
            manifest = load_manifest(args.manifest)
            for j in manifest.get("jobs", []):
                launcher.start(j.get("name"))
            print("Launcher running in continuous mode. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
        else:
            print("Invalid command or missing --job argument")
    except KeyboardInterrupt:
        print("\nShutting down...")
        launcher.shutdown()

if __name__ == "__main__":
    main()
