#!/usr/bin/env python3
"""
Operator Dashboard Backend
- serves the operator UI
- exposes restful endpoints for:
  - operators: list suggestions, approve them
  - updater: list staged artifacts, promote
  - marketplace: search plugins, install/uninstall
  - audit logs
This backend is *local-first* and can be run on Aurora Core machine.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import shutil, os, json, time, subprocess

ROOT = Path(__file__).resolve().parents[2]
UI_DIR = ROOT / "integration" / "dashboard" / "static"
UPDATER_DIR = ROOT / "integration" / "updater"
MARKET = ROOT / "integration" / "marketplace"
AUDIT_LOG = ROOT / "integration" / "audit.log"

app = FastAPI(title="Aurora Operator Dashboard")

# mount static UI
if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")

# endpoints
@app.get("/api/updater/list")
def list_staged():
    staged = [d.name for d in (UPDATER_DIR / ".aurora_updates" / "staging").glob("*") if d.is_dir()] if (UPDATER_DIR / ".aurora_updates" / "staging").exists() else []
    return {"staged": staged}

@app.post("/api/updater/upload")
async def upload(artifact: UploadFile = File(...)):
    data = await artifact.read()
    tmp = UPDATER_DIR / artifact.filename
    tmp.write_bytes(data)
    # optionally auto-sign (not here) - operator must verify
    return {"ok": True, "filename": str(tmp)}

@app.post("/api/updater/stage")
def stage_file(filename: str = Form(...)):
    # uses updater_service.stage_artifact if available; otherwise do manual copy
    from integration.updater.updater_service import stage_artifact, STAGING
    src = UPDATER_DIR / filename
    if not src.exists():
        raise HTTPException(404, "file not found")
    dest = stage_artifact(src)
    return {"ok": True, "staging": str(dest)}

@app.get("/api/suggestions/list")
def suggestions_list():
    # aggregate suggestions from agents + automotive/maritime/aviation folders
    roots = [Path("agents/suggestions"), Path("automotive/suggestions"), Path("aviation/suggestions")]
    out = {}
    for r in roots:
        if r.exists():
            out[str(r)] = [p.name for p in sorted(r.iterdir()) if p.is_file()]
    return out

@app.post("/api/suggestions/approve")
def approve(file: str):
    # find file and mark approved (very minimal here)
    p = Path(file)
    if not p.exists():
        raise HTTPException(404,"not found")
    p.with_suffix(p.suffix + ".approved").write_text(json.dumps({"ts":time.time()}))
    with open(AUDIT_LOG,"a") as fh:
        fh.write(f"{time.time()} APPROVE {file}\n")
    return {"ok": True}

# Marketplace: simple local-first plugin marketplace
@app.get("/api/marketplace/list")
def marketplace_list():
    # list available plugin archives in marketplace/catalog
    catalog = MARKET / "catalog"
    if not catalog.exists():
        return {"catalog": []}
    return {"catalog": [p.name for p in catalog.iterdir() if p.is_file()]}

@app.post("/api/marketplace/install")
def marketplace_install(pkg_name: str):
    # install plugin package into aurora_modules
    src = MARKET / "catalog" / pkg_name
    if not src.exists():
        raise HTTPException(404, "package not found")
    import tarfile
    with tarfile.open(src, "r:*") as tf:
        tf.extractall("aurora_modules")
    with open(AUDIT_LOG,"a") as fh: fh.write(f"{time.time()} INSTALL {pkg_name}\n")
    return {"ok": True}

@app.get("/api/audit/last")
def audit_last(n: int = 200):
    if not Path(AUDIT_LOG).exists(): return {"lines": []}
    lines = Path(AUDIT_LOG).read_text().splitlines()[-n:]
    return {"lines": lines}

# serve dashboard UI
@app.get("/")
def root():
    if (UI_DIR / "index.html").exists():
        return FileResponse(UI_DIR / "index.html")
    return JSONResponse({"ok": True, "msg": "operator dashboard running"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("integration.dashboard.backend:app", host="0.0.0.0", port=9711, reload=False)
