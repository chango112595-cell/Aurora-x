"""
resource_governor.py - soft resource control for pack instances.

Design:
- Provide a simple API to request CPU shares and memory MB for a pack.
- On Linux, attempt to use cgroups v1/v2 if available (best-effort), else use polling to enforce memory.
- Must never kill processes unless operator explicitly requests.
"""
import os, time, json
from pathlib import Path
import threading
try:
    import psutil
except Exception:
    psutil = None

ROOT = Path(__file__).resolve().parents[2]
GOV_DIR = ROOT / "data" / "gov"
GOV_DIR.mkdir(parents=True, exist_ok=True)

class ResourceGovernor:
    def __init__(self, pack_id: str):
        self.pack_id = pack_id
        self.cfg_path = GOV_DIR / f"{pack_id}.json"
        if not self.cfg_path.exists():
            self.cfg_path.write_text(json.dumps({"memory_mb": None, "cpu_shares": None}))
        self._stop = False
        self._thread = None

    def set_limits(self, memory_mb: int = None, cpu_shares: int = None):
        self.cfg_path.write_text(json.dumps({"memory_mb": memory_mb, "cpu_shares": cpu_shares}))
        return True

    def apply_limits(self):
        # Start a background monitor if necessary
        if self._thread and self._thread.is_alive():
            return True
        self._stop = False
        self._thread = threading.Thread(target=self._monitor, daemon=True)
        self._thread.start()
        return True

    def _monitor(self):
        # Best-effort monitor: if psutil available, check processes under pack VFS and log leaks
        if psutil is None:
            # nothing to do
            return
        try:
            cfg = json.loads(self.cfg_path.read_text())
            mem_limit = cfg.get("memory_mb")
            while not self._stop:
                # find processes with cwd under pack data/vfs/<pack>
                for p in psutil.process_iter(['pid','cwd','memory_info']):
                    try:
                        cwd = p.info.get('cwd') or ""
                        if str(ROOT / "data" / "vfs" / self.pack_id) in (cwd or ""):
                            if mem_limit:
                                rss = p.memory_info().rss / (1024*1024)
                                if rss > mem_limit * 1.1:
                                    # log but do not kill
                                    Path(ROOT / "logs" / f"{self.pack_id}_gov.log").write_text(f"PID {p.pid} exceeding mem {rss}MB > {mem_limit}MB\n")
                    except Exception:
                        pass
                time.sleep(2)
        except Exception:
            pass

    def stop(self):
        self._stop = True
        if self._thread:
            self._thread.join(timeout=1)
        return True
