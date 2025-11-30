#!/usr/bin/env python3
"""
AuroraOS universal orchestrator
- start/stop/restart/status
- built-in REST control API (FastAPI) [optional]
- watchdog + auto-heal
- hot-reload (dev) mode (optional)
- logs & metrics
- PM2 fallback available via tools/aurora-cli.js (optional)
"""

import os
import sys
import subprocess
import threading
import time
import signal
import json
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

# Optional packages (FastAPI / uvicorn / psutil / watchdog)
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import FileResponse
    import uvicorn
    import psutil
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    HAS_WEB = True
except Exception:
    HAS_WEB = False

ROOT = Path(__file__).resolve().parents[0]
LOG_DIR = ROOT / "aurora_logs"
PID_DIR = ROOT / ".aurora" / "pids"
LOG_DIR.mkdir(parents=True, exist_ok=True)
PID_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Configuration ----------
# Replace these commands if your paths differ.
APPS = {
    "core": ["python3", "tools/aurora_core.py"],
    "nexus_v3": ["python3", "aurora_nexus_v3/main.py"],
    "nexus_v2": ["python3", "tools/luminar_nexus_v2.py", "serve"],
    "express": ["npx", "tsx", "server/index.ts"]
}

# REST API token (change for production)
API_TOKEN = os.environ.get("AURORA_API_TOKEN", "aurora-dev-token")

# Watchdog settings
WATCHDOG_INTERVAL = float(os.environ.get("AURORA_WATCHDOG_INTERVAL", "2.0"))
RESTART_ON_CRASH = os.environ.get("AURORA_RESTART_ON_CRASH", "1") == "1"
HOTRELOAD_EXTS = tuple(os.environ.get("AURORA_HOTRELOAD_EXTS", ".py,.ts,.tsx,.js").split(","))

# ---------- Utilities ----------
def now_ts(): return datetime.utcnow().isoformat() + "Z"
def log_write(service, msg):
    p = LOG_DIR / f"{service}.log"
    with open(p, "a", encoding="utf8") as fh:
        fh.write(f"{now_ts()} {msg}\n")
def pid_file(name): return PID_DIR / f"{name}.pid"
def write_pid(name, pid): pid_file(name).write_text(str(pid))
def read_pid(name) -> Optional[int]:
    p = pid_file(name)
    if p.exists():
        try:
            return int(p.read_text().strip())
        except:
            return None
    return None
def remove_pid(name):
    try: pid_file(name).unlink()
    except: pass

# ---------- Process control ----------
PROCS: Dict[str, subprocess.Popen] = {}
LOCK = threading.Lock()

def spawn_app(name, cmd, env=None):
    log_write(name, f"spawn requested: {' '.join(cmd)}")
    outf = open(LOG_DIR / f"{name}.out.log", "a")
    errf = open(LOG_DIR / f"{name}.err.log", "a")
    # On Windows you might want shell=True and cmd as string; keep safe default.
    proc = subprocess.Popen(cmd, stdout=outf, stderr=errf, cwd=str(ROOT), env=env or os.environ.copy())
    PROCS[name] = proc
    write_pid(name, proc.pid)
    log_write(name, f"spawned pid={proc.pid}")
    return proc

def start(name):
    with LOCK:
        if name in PROCS and PROCS[name].poll() is None:
            return {"ok": False, "msg": f"{name} already running"}
        cmd = APPS.get(name)
        if not cmd:
            return {"ok": False, "msg": "unknown service"}
        spawn_app(name, cmd)
        time.sleep(0.4)
        return {"ok": True}

def stop(name, timeout=5):
    with LOCK:
        pid = read_pid(name)
        proc = PROCS.get(name)
        # If we have only pid, try psutil to terminate
        if not proc and pid:
            try:
                p = psutil.Process(pid)
                log_write(name, f"terminating external pid {pid}")
                p.terminate()
                p.wait(timeout=timeout)
                remove_pid(name)
                return {"ok": True}
            except Exception:
                pass
        if not proc:
            remove_pid(name)
            return {"ok": False, "msg": "not running"}
        try:
            proc.terminate()
            proc.wait(timeout=timeout)
        except Exception:
            try: proc.kill()
            except: pass
        remove_pid(name)
        PROCS.pop(name, None)
        log_write(name, "stopped")
        return {"ok": True}

def start_all(order=None):
    order = order or ["core", "nexus_v3", "nexus_v2", "express"]
    results = {}
    for n in order:
        results[n] = start(n)
        time.sleep(0.6)
    return results

def stop_all():
    results = {}
    for n in list(APPS.keys())[::-1]:
        results[n] = stop(n)
    return results

# ---------- Watchdog and auto-heal ----------
WATCHDOG_ENABLED = True
def _health_check_loop():
    while WATCHDOG_ENABLED:
        time.sleep(WATCHDOG_INTERVAL)
        for name, proc in list(PROCS.items()):
            if proc.poll() is not None:
                log_write(name, f"CRASH detected (code {proc.returncode})")
                PROCS.pop(name, None)
                remove_pid(name)
                if RESTART_ON_CRASH:
                    try:
                        log_write(name, "auto-restarting")
                        spawn_app(name, APPS[name])
                    except Exception as e:
                        log_write(name, f"restart failed: {e}")
        # system metrics
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            log_write("system", f"cpu={cpu} mem={mem}")
        except Exception:
            pass

def start_watchdog():
    t = threading.Thread(target=_health_check_loop, daemon=True)
    t.start()

# ---------- Hot-reload (dev) ----------
if HAS_WEB:
    class CodeChangeHandler(FileSystemEventHandler):
        def __init__(self, callback):
            self.callback = callback
            self._last = 0
        def on_any_event(self, event):
            if event.is_directory: return
            if not any(event.src_path.endswith(ext) for ext in HOTRELOAD_EXTS): return
            now = time.time()
            if now - self._last < 1.0: return
            self._last = now
            log_write("hotreload", f"change {event.src_path}")
            try: self.callback()
            except Exception as e: log_write("hotreload", f"callback error: {e}")

    def start_hotreload(restart_cb):
        obs = Observer()
        h = CodeChangeHandler(restart_cb)
        obs.schedule(h, path=str(ROOT), recursive=True)
        obs.daemon = True
        obs.start()
        return obs

# ---------- REST control API (optional) ----------
app = None
if HAS_WEB:
    app = FastAPI(title="AuroraOS Control API")
    def auth_ok(req: Request):
        h = req.headers.get("authorization","")
        if not h.startswith("Bearer "): raise HTTPException(status_code=401, detail="Missing auth")
        token = h.split(" ",1)[1]
        if token != API_TOKEN: raise HTTPException(status_code=403, detail="Invalid token")

    @app.get("/api/status")
    def api_status(request: Request):
        auth_ok(request)
        out = {}
        for name in APPS:
            pid = read_pid(name)
            out[name] = {"pid": pid, "running": pid is not None}
        return out

    @app.post("/api/start/{name}")
    def api_start(name: str, request: Request):
        auth_ok(request)
        if name == "all": return start_all()
        return start(name)

    @app.post("/api/stop/{name}")
    def api_stop(name: str, request: Request):
        auth_ok(request)
        if name == "all": return stop_all()
        return stop(name)

    @app.get("/api/log/{name}")
    def api_log(name: str, request: Request):
        auth_ok(request)
        p = LOG_DIR / f"{name}.out.log"
        if not p.exists(): raise HTTPException(status_code=404)
        return FileResponse(p)

# ---------- CLI entrypoint ----------
def usage():
    print("Usage: aurora_os.py <start|stop|restart|status|runserver|hotdev>")
    print(" env: AURORA_API_TOKEN=... to set API token")

def run_server_blocking(host="0.0.0.0", port=9701):
    if not HAS_WEB:
        print("Missing FastAPI dependencies. Install: pip install fastapi uvicorn[standard] psutil watchdog")
        return
    uvicorn.run(app, host=host, port=port, log_level="info")

def main():
    if len(sys.argv) < 2:
        usage(); return
    cmd = sys.argv[1].lower()
    if cmd == "start":
        start_all()
        start_watchdog()
        print("Aurora started")
    elif cmd == "stop":
        global WATCHDOG_ENABLED
        WATCHDOG_ENABLED = False
        stop_all()
        print("Aurora stopped")
    elif cmd == "restart":
        stop_all(); time.sleep(1); start_all()
    elif cmd == "status":
        for name in APPS:
            pid = read_pid(name)
            print(f"{name}: pid={pid}")
    elif cmd == "runserver":
        run_server_blocking()
    elif cmd == "hotdev":
        start_all()
        def restart_cb():
            # hotdev restarts express and core only (you may change)
            try:
                stop("express"); stop("core")
                time.sleep(0.6)
                start("core"); start("express")
            except Exception as e:
                log_write("hotdev", f"hotdev restart err: {e}")
        obs = start_hotreload(restart_cb)
        print("Hotdev running - Ctrl+C to exit")
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            stop_all()
            obs.stop()
    else:
        usage()

if __name__ == "__main__":
    main()
