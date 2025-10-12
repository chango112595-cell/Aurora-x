from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

PWA_DIR = Path('frontend/pwa')

def attach_pwa(app: FastAPI):
    @app.get("/manifest.webmanifest")
    def manifest():
        path = PWA_DIR / "manifest.webmanifest"
        if not path.exists():
            return JSONResponse({"ok": False, "err": "manifest missing"}, status_code=404)
        return FileResponse(path, media_type="application/manifest+json")

    @app.get("/service-worker.js")
    def sw():
        path = PWA_DIR / "service-worker.js"
        if not path.exists():
            return JSONResponse({"ok": False, "err": "sw missing"}, status_code=404)
        return FileResponse(path, media_type="application/javascript")