
#!/usr/bin/env python3
import os
import json
import asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import subprocess
from fastapi.responses import JSONResponse

app = FastAPI(title="Aurora MCP Server")

class FSReadReq(BaseModel):
    path: str

class FSWriteReq(BaseModel):
    path: str
    content: str

class FSListReq(BaseModel):
    path: str

class ProcessRunReq(BaseModel):
    cmd: str
    shell: bool = False
    timeout: int | None = 30

@app.post("/fs/read")
async def fs_read(req: FSReadReq):
    p = Path(req.path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="file not found")
    text = p.read_text(encoding="utf-8", errors="ignore")
    return {"path": str(p), "content": text}

@app.post("/fs/write")
async def fs_write(req: FSWriteReq):
    p = Path(req.path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(req.content, encoding="utf-8")
    return {"path": str(p), "written": True}

@app.post("/fs/list")
async def fs_list(req: FSListReq):
    p = Path(req.path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="path not found")
    entries = []
    for child in sorted(p.iterdir()):
        entries.append({"name": child.name, "is_file": child.is_file(), "is_dir": child.is_dir()})
    return {"path": str(p), "entries": entries}

@app.post("/process/run")
async def process_run(req: ProcessRunReq):
    try:
        completed = subprocess.run(
            req.cmd if req.shell else req.cmd.split(),
            shell=req.shell,
            capture_output=True,
            text=True,
            timeout=req.timeout,
        )
        return {
            "cmd": req.cmd,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except subprocess.TimeoutExpired as e:
        return JSONResponse(status_code=504, content={"error": "timeout", "detail": str(e)})

@app.get("/")
async def index():
    return {"status": "running", "port": os.environ.get("PORT")}

class ConnectionManager:
    def __init__(self):
        self.active = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active.discard(websocket)

    async def send_json(self, websocket: WebSocket, data):
        await websocket.send_text(json.dumps(data))

manager = ConnectionManager()

@app.websocket("/mcp")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except Exception:
                await manager.send_json(websocket, {"error": "invalid_json", "raw": data})
                continue

            typ = msg.get("type")

            if typ == "fs_read":
                path = msg.get("path")
                if not path:
                    await manager.send_json(websocket, {"error": "missing_path"})
                    continue
                p = Path(path)
                if not p.exists():
                    await manager.send_json(websocket, {"error": "not_found", "path": path})
                    continue
                content = p.read_text(encoding="utf-8", errors="ignore")
                await manager.send_json(websocket, {"type": "fs_read_resp", "path": str(p), "content": content})

            elif typ == "fs_list":
                path = msg.get("path", ".")
                p = Path(path)
                if not p.exists():
                    await manager.send_json(websocket, {"error": "not_found", "path": path})
                    continue
                entries = [
                    {"name": c.name, "is_file": c.is_file(), "is_dir": c.is_dir()}
                    for c in sorted(p.iterdir())
                ]
                await manager.send_json(websocket, {"type": "fs_list_resp", "path": str(p), "entries": entries})

            elif typ == "run":
                cmd = msg.get("cmd")
                if not cmd:
                    await manager.send_json(websocket, {"error": "missing_cmd"})
                    continue
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                await manager.send_json(
                    websocket,
                    {
                        "type": "run_resp",
                        "cmd": cmd,
                        "returncode": proc.returncode,
                        "stdout": stdout.decode(),
                        "stderr": stderr.decode(),
                    },
                )

            else:
                await manager.send_json(websocket, {"error": "unknown_type", "received": msg})

    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=port)
