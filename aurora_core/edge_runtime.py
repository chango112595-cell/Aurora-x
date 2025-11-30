#!/usr/bin/env python3
"""
Aurora Edge runtime - minimal footprint runtime for constrained devices.
Connects to local AuroraLink hub (or to a central core) and responds to commands.
"""

import asyncio
import json
import os
import time
from pathlib import Path
try:
    import websockets
except:
    websockets = None

AURORA_LINK = os.environ.get("AURORA_LINK", "ws://127.0.0.1:9801")
ID = os.environ.get("AURORA_EDGE_ID", f"edge-{os.getpid()}")

async def run():
    if not websockets:
        print("websockets missing; pip install websockets")
        return
    async with websockets.connect(AURORA_LINK) as ws:
        await ws.send(json.dumps({"type":"hello","id":ID}))
        while True:
            msg = await ws.recv()
            obj = json.loads(msg)
            # very simple: respond to ping
            if obj.get("type") == "ping":
                await ws.send(json.dumps({"type":"pong","id":ID, "ts": time.time()}))

if __name__ == "__main__":
    asyncio.run(run())
