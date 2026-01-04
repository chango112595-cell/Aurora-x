import os

from fastapi import FastAPI

app = FastAPI()


@app.get("/api/health")
def h():
    return {"ok": True}


@app.get("/api/packs")
def p():
    return {"packs": [d for d in os.listdir("packs") if d.startswith("pack")]}
