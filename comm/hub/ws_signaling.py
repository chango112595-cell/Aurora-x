#!/usr/bin/env python3
"""
Simple WebSocket signaling server using websockets lib
"""

import asyncio

try:
    import websockets
except Exception:
    websockets = None

CLIENTS = set()


async def handler(ws, path):
    CLIENTS.add(ws)
    try:
        async for msg in ws:
            # echo to all (simple)
            for c in list(CLIENTS):
                if c != ws:
                    await c.send(msg)
    finally:
        CLIENTS.remove(ws)


def run(port=9704):
    if not websockets:
        print("Install websockets for ws_signaling")
        return
    asyncio.get_event_loop().run_until_complete(websockets.serve(handler, "0.0.0.0", port))
    print("WebSocket signaling running on", port)
    asyncio.get_event_loop().run_forever()
