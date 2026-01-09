#!/usr/bin/env python3
"""
Small FastAPI backend to serve Quantum UI and control agents/memory.
This integrates agents and memory from the packages above.
"""

from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, PlainTextResponse

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "ui" / "quantum_ui" / "static"
app = FastAPI(title="Aurora Quantum UI API")


# lazy imports to avoid circular dependencies
def get_agent_manager():
    try:
        from agents.agent_core import Agent, Tool
        from agents.agent_manager import AgentManager
        from agents.tools.shell_tool import shell_call
        from memory.vecstore import MemoryStore
    except Exception as e:
        raise RuntimeError("Missing modules: " + str(e))
    mem = MemoryStore()
    tools = {"shell": Tool("shell", shell_call)}
    agent = Agent("default", mem, tools, policy={"human_in_loop": True})
    mgr = AgentManager(max_workers=2)
    mgr.start()
    return {"mgr": mgr, "agent": agent, "mem": mem}


STATE = get_agent_manager()


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/agents")
def agents_list():
    a = STATE["agent"]
    return [{"id": a.id, "name": a.name}]


@app.post("/api/agents/run")
async def run_agent(req: Request):
    payload = await req.json()
    goal = payload.get("goal", "")
    results = STATE["agent"].run(goal)
    return {"ok": True, "results": results}


@app.get("/api/memory/search")
def search(q: str = ""):
    mem = STATE["mem"]
    res = mem.search(q, top_k=10)
    return res


@app.get("/api/sys/log")
def syslog(lines: int = 200):
    p = Path("aurora_logs/orchestrator.log")
    if not p.exists():
        return PlainTextResponse("")
    data = p.read_text().splitlines()[-lines:]
    return PlainTextResponse("\n".join(data))


if __name__ == "__main__":
    uvicorn.run("ui.quantum_ui.backend:app", host="0.0.0.0", port=9702, reload=False)
