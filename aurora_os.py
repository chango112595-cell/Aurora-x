#!/usr/bin/env python3
"""
AuroraOS universal orchestrator
- start/stop/restart/status
- built-in REST control API (FastAPI)
- watchdog + auto-heal
- hot-reload (dev) mode (optional)
- logs & metrics
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

# ---- optional deps: fastapi, uvicorn, psutil, watchdog
# pip install fastapi "uvicorn[standard]" psutil watchdog

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse, FileResponse
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

# --- Configuration: set your commands here
# Keep them exact as you provided earlier.
APPS = {
    "core": ["python3", "tools/aurora_core.py"],
    "nexus_v3": ["python3", "aurora_nexus_v3/main.py"],
    "nexus_v2": ["python3", "tools/luminar_nexus_v2.py", "serve"],
    "express": ["npx", "tsx", "server/index.ts"]
}

# REST API auth token (change on install)
API_TOKEN = os.environ.get("AURORA_API_TOKEN", "aurora-dev-token")

# ------------- helpers -------------
def now_ts():
    return datetime.utcnow().isoformat() + "Z"

def log_write(name, msg):
    p = LOG_DIR / f"{name}.log"
    with open(p, "a", encoding="utf8") as fh:
        fh.write(f"{now_ts()} {msg}\n")

def pid_file(name):
    return PID_DIR / f"{name}.pid"

def write_pid(name, pid):
    pid_file(name).write_text(str(pid))

def read_pid(name) -> Optional[int]:
    p = pid_file(name)
    if p.exists():
        try:
            return int(p.read_text().strip())
        except:
            return None
    return None

def remove_pid(name):
    try:
        pid_file(name).unlink()
    except:
        pass

# ------------- process management -------------
PROCS: Dict[str, subprocess.Popen] = {}
LOCK = threading.Lock()

def spawn_app(name, cmd, env=None):
    out = open(LOG_DIR / f"{name}.out.log", "a")
    err = open(LOG_DIR / f"{name}.err.log", "a")
    # use shell=False for safety; on Windows ensure 'python3' may be 'python'
    process = subprocess.Popen(cmd, stdout=out, stderr=err, cwd=str(ROOT), env=env or os.environ.copy())
    PROCS[name] = process
    write_pid(name, process.pid)
    log_write(name, f"spawned pid={process.pid} cmd={' '.join(cmd)}")
    return process

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
        if not proc and pid:
            try:
                proc = psutil.Process(pid)
            except Exception:
                proc = None
        if not proc:
            remove_pid(name)
            return {"ok": False, "msg": "not running"}
        try:
            log_write(name, "terminating")
            if isinstance(proc, subprocess.Popen):
                proc.terminate()
                proc.wait(timeout=timeout)
            else:
                proc.terminate()
                proc.wait(timeout=timeout)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        remove_pid(name)
        PROCS.pop(name, None)
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

# ------------- watchdog & auto-heal -------------
WATCHDOG_ENABLED = True
WATCHDOG_INTERVAL = 2.0
RESTART_ON_CRASH = True

def _health_check_loop():
    while WATCHDOG_ENABLED:
        time.sleep(WATCHDOG_INTERVAL)
        for name, proc in list(PROCS.items()):
            if proc.poll() is not None:
                log_write(name, f"process {name} exited with code {proc.returncode}")
                PROCS.pop(name, None)
                remove_pid(name)
                if RESTART_ON_CRASH:
                    log_write(name, "auto-restarting after crash")
                    try:
                        spawn_app(name, APPS[name])
                    except Exception as e:
                        log_write(name, f"restart failed: {e}")

def start_watchdog():
    t = threading.Thread(target=_health_check_loop, daemon=True)
    t.start()

# ------------- hot-reload (dev) -------------
class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, restart_callback, watch_exts=(".py", ".ts", ".tsx", ".js")):
        self.restart_cb = restart_callback
        self.watch_exts = watch_exts
        self._last = 0

    def on_any_event(self, event):
        if event.is_directory:
            return
        if not any(event.src_path.endswith(ext) for ext in self.watch_exts):
            return
        now = time.time()
        # debounce
        if now - self._last < 1.0:
            return
        self._last = now
        log_write("hotreload", f"file changed: {event.src_path}")
        self.restart_cb()

def start_hotreload(path=".", restart_callback=None):
    observer = Observer()
    handler = CodeChangeHandler(restart_callback or (lambda: None))
    observer.schedule(handler, path=str(ROOT), recursive=True)
    observer.daemon = True
    observer.start()
    return observer

# ------------- REST API (control & status) -------------
app = None
if HAS_WEB:
    app = FastAPI(title="AuroraOS Control API")

    def api_auth(request: Request):
        token = request.headers.get("authorization") or request.query_params.get("token")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Bearer token")
        token = token.split(" ",1)[1]
        if token != API_TOKEN:
            raise HTTPException(status_code=403, detail="Invalid token")

    @app.get("/api/status")
    def api_status(token: str = None, request: Request = None):
        # simple auth
        h = request.headers.get("authorization","")
        if not h.startswith("Bearer ") or h.split(" ",1)[1] != API_TOKEN:
            raise HTTPException(status_code=401)
        status = {}
        for name in APPS:
            pid = read_pid(name)
            status[name] = {"pid": pid, "running": (pid is not None)}
        return status

    @app.post("/api/start/{name}")
    def api_start(name: str, request: Request):
        h = request.headers.get("authorization","")
        if not h.startswith("Bearer ") or h.split(" ",1)[1] != API_TOKEN:
            raise HTTPException(status_code=401)
        if name == "all": 
            return start_all()
        return start(name)

    @app.post("/api/stop/{name}")
    def api_stop(name: str, request: Request):
        h = request.headers.get("authorization","")
        if not h.startswith("Bearer ") or h.split(" ",1)[1] != API_TOKEN:
            raise HTTPException(status_code=401)
        if name == "all":
            return stop_all()
        return stop(name)

    @app.get("/api/log/{name}")
    def api_log(name: str, request: Request):
        h = request.headers.get("authorization","")
        if not h.startswith("Bearer ") or h.split(" ",1)[1] != API_TOKEN:
            raise HTTPException(status_code=401)
        p = LOG_DIR / f"{name}.out.log"
        if not p.exists():
            raise HTTPException(status_code=404)
        return FileResponse(p)

# ------------- CLI entrypoint -------------
def usage():
    print("Usage: aurora_os.py <start|stop|restart|status|api-start|api-stop|api-status|runserver|hotdev>")
    print(" env: AURORA_API_TOKEN=... to set API token")
    print("Note: runserver will start the REST API + dashboard (if FastAPI deps installed)")

def run_server_blocking(host="0.0.0.0", port=9701):
    if not HAS_WEB:
        print("FastAPI/uvicorn not installed (pip install fastapi uvicorn psutil watchdog)")
        return
    uvicorn.run(app, host=host, port=port, log_level="info")

def restart_all():
    stop_all()
    time.sleep(1)
    start_all()

def main():
    start_watchdog()
    if len(sys.argv) < 2:
        usage(); return
    cmd = sys.argv[1].lower()
    if cmd == "start":
        start_all()
        start_watchdog()
        print("Aurora started")
    elif cmd == "stop":
        stop_all()
        print("Aurora stopped")
    elif cmd == "restart":
        restart_all()
    elif cmd == "status":
        for name in APPS:
            pid = read_pid(name)
            print(f"{name}: pid={pid}")
    elif cmd == "runserver":
        # run REST API + dashboard
        if not HAS_WEB:
            print("Missing fastapi/uvicorn. Install: pip install fastapi uvicorn[standard] psutil watchdog")
            return
        run_server_blocking()
    elif cmd == "hotdev":
        # start everything, enable hot reload (dev)
        start_all()
        def restart_cb():
            print("Hot-reload triggered — restarting express & ai core")
            stop("express")
            stop("core")
            time.sleep(0.5)
            start("core")
            start("express")
        start_hotreload(restart_callback=restart_cb)
        print("Hotdev running — press Ctrl+C to exit")
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            stop_all()
    else:
        usage()

if __name__ == "__main__":
    main()
