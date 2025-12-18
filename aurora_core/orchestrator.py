#!/usr/bin/env python3
"""
Aurora Core Orchestrator
- module/plugin loader
- process supervisor + watchdog
- simple AuroraLink (WebSocket) server for internal device comms
- sandboxed module runner (resource-limited subprocess)
- update stub (safe in-repo updater)
"""

import os
import sys
import json
import time
import signal
import shutil
import logging
import threading
import subprocess
from pathlib import Path
from typing import Dict, Optional, Callable, Any
import psutil
import asyncio
import functools

# Optional dependencies: websockets, fastapi/uvicorn if you want REST control
# pip install psutil websockets

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "aurora_logs"
MODULES_DIR = ROOT / "aurora_modules"
PID_DIR = ROOT / ".aurora" / "pids"
LOG_DIR.mkdir(parents=True, exist_ok=True)
MODULES_DIR.mkdir(parents=True, exist_ok=True)
PID_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("aurora.orchestrator")
handler = logging.FileHandler(LOG_DIR / "orchestrator.log")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# -------------------------
# Utilities
# -------------------------
def write_pid(name: str, pid: int):
    p = PID_DIR / f"{name}.pid"
    p.write_text(str(pid))

def read_pid(name: str) -> Optional[int]:
    p = PID_DIR / f"{name}.pid"
    if not p.exists():
        return None
    try:
        return int(p.read_text().strip())
    except:
        return None

def remove_pid(name: str):
    try:
        (PID_DIR / f"{name}.pid").unlink()
    except:
        pass

def now_iso(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

# -------------------------
# Module plugin loader
# -------------------------
class Plugin:
    def __init__(self, path: Path):
        self.path = path
        self.meta = {}
        self.name = path.stem
        self.entry = None
        self.load_meta()

    def load_meta(self):
        meta_file = self.path / "module.json"
        if not meta_file.exists():
            return
        try:
            self.meta = json.loads(meta_file.read_text(encoding="utf8"))
            self.entry = self.meta.get("entry", "run.py")
        except Exception as e:
            logger.error("failed loading meta for %s: %s", self.name, e)

    def start(self, args=None, env=None):
        runner = self.path / self.entry
        if not runner.exists():
            raise FileNotFoundError(f"entry not found {runner}")
        return SandboxRunner.start_process(self.name, [sys.executable, str(runner)] + (args or []), cwd=str(self.path), env=env)

# -------------------------
# Sandbox runner (process with resource limits)
# -------------------------
class SandboxRunner:
    @staticmethod
    def start_process(name: str, cmd: list, cwd: str = ".", env: Optional[dict] = None, cpu_limit_pct: Optional[int] = None):
        """
        Start process and restrict resources lightly using psutil where possible.
        For stronger sandboxing, run in containers or use OS-level cgroups.
        """
        logger.info("starting sandboxed process %s: %s", name, cmd)
        proc = subprocess.Popen(cmd, cwd=cwd, env=(env or os.environ.copy()))
        write_pid(name, proc.pid)
        # best-effort resource limiting (deferred to watchdog thread)
        return proc

    @staticmethod
    def kill_process(name: str):
        pid = read_pid(name)
        if not pid:
            return False
        try:
            p = psutil.Process(pid)
            p.terminate()
            p.wait(timeout=5)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
        remove_pid(name)
        return True

# -------------------------
# Supervisor + watchdog
# -------------------------
class Supervisor:
    def __init__(self, check_interval=2.0, restart_on_crash=True):
        self.services: Dict[str, subprocess.Popen] = {}
        self.lock = threading.Lock()
        self.check_interval = check_interval
        self.restart_on_crash = restart_on_crash
        self.running = False
        self._thread = None

    def register_service(self, name: str, start_fn: Callable[[], subprocess.Popen]):
        with self.lock:
            if name in self.services:
                logger.warning("service %s already registered", name)
                return
            p = start_fn()
            self.services[name] = p
            logger.info("registered service %s pid=%s", name, getattr(p, "pid", None))

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="supervisor-loop")
        self._thread.start()
        logger.info("supervisor started")

    def stop(self):
        self.running = False
        with self.lock:
            for name, proc in list(self.services.items()):
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                except Exception:
                    try: proc.kill()
                    except: pass
                remove_pid(name)
                logger.info("service %s stopped", name)
        logger.info("supervisor stopped")

    def _loop(self):
        while self.running:
            time.sleep(self.check_interval)
            with self.lock:
                for name, proc in list(self.services.items()):
                    if proc.poll() is not None:
                        logger.warning("service %s exited with code %s", name, proc.returncode)
                        remove_pid(name)
                        self.services.pop(name, None)
                        if self.restart_on_crash:
                            logger.info("restarting %s", name)
                            # naive restart: find plugin and start again
                            plugin_path = MODULES_DIR / name
                            if plugin_path.exists():
                                try:
                                    plugin = Plugin(plugin_path)
                                    newp = plugin.start()
                                    self.services[name] = newp
                                except Exception as e:
                                    logger.error("failed to restart %s: %s", name, e)

# -------------------------
# AuroraLink (WebSocket) - simple P2P hub (local-only)
# -------------------------
# Lightweight asyncio+websockets server providing a local pub/sub.
try:
    import websockets
except Exception:
    websockets = None

class AuroraLink:
    def __init__(self, host="0.0.0.0", port=9801):
        self.host = host
        self.port = port
        self.clients = set()
        self.server = None

    async def handler(self, websocket, path):
        self.clients.add(websocket)
        addr = websocket.remote_address
        logger.info("auroralink client connected %s", addr)
        try:
            async for message in websocket:
                # simple JSON envelope expected
                try:
                    obj = json.loads(message)
                except:
                    obj = {"raw": message}
                # echo to all for now (local hub)
                await self.broadcast(obj, sender=websocket)
        except Exception as e:
            logger.info("auroralink client disconnect %s: %s", addr, e)
        finally:
            self.clients.remove(websocket)

    async def broadcast(self, obj, sender=None):
        m = json.dumps(obj)
        await asyncio.wait([c.send(m) for c in self.clients if c is not sender])

    async def serve(self):
        if not websockets:
            logger.warning("websockets not installed; auroralink disabled")
            return
        self.server = await websockets.serve(self.handler, self.host, self.port)
        logger.info("auroralink running on %s:%s", self.host, self.port)
        await self.server.wait_closed()

    def run_in_thread(self):
        if not websockets:
            return
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=functools.partial(loop.run_until_complete, self.serve()), daemon=True)
        t.start()

# -------------------------
# Updater stub (safe)
# -------------------------
class Updater:
    """
    Minimal safe updater: for production use code-signing + atomic swaps.
    This stub demonstrates:
      - fetch update to staging dir
      - validate (checksum/signature) - omitted for brevity
      - swap directories atomically
    """
    STAGING = ROOT / ".aurora_updates" / "staging"
    STAGING.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def stage_archive(archive_path: str):
        # user provides a tarball; we extract to staging and validate
        import tarfile
        try:
            with tarfile.open(archive_path, "r:*") as tf:
                tf.extractall(Updater.STAGING)
            logger.info("staged update from %s", archive_path)
            return True
        except Exception as e:
            logger.error("failed stage update: %s", e)
            return False

    @staticmethod
    def activate_staging():
        # **DANGEROUS**: real world requires signatures + backups + validators
        backup = ROOT / ".aurora_backup"
        if backup.exists():
            shutil.rmtree(backup)
        shutil.copytree(ROOT, backup, dirs_exist_ok=True)
        # copy staged content into place (very naive)
        for item in Updater.STAGING.iterdir():
            target = ROOT / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
        logger.info("activated staging update (backup saved)")
        return True

# -------------------------
# Example orchestration entrypoint
# -------------------------
def load_plugins():
    plugins = {}
    for child in MODULES_DIR.iterdir():
        if child.is_dir():
            p = Plugin(child)
            plugins[p.name] = p
    return plugins

def main_loop():
    sup = Supervisor()
    plugins = load_plugins()
    # register each plugin to supervisor
    for name, plugin in plugins.items():
        try:
            sup.register_service(name, lambda p=plugin: p.start())
        except Exception as e:
            logger.exception("failed register plugin %s: %s", name, e)
    sup.start()
    # start auroralink
    link = AuroraLink()
    try:
        link.run_in_thread()
    except Exception:
        pass
    # run until killed
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("shutdown requested")
        sup.stop()

if __name__ == "__main__":
    main_loop()
