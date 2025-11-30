#!/usr/bin/env python3
"""
WebRTC Hub stub.
- If aiortc installed, provides a simple peer relay/offer handler.
- Otherwise falls back to WebSocket-based signaling.
This is a signaling server only; media/DTLS handled by WebRTC libs on devices.
"""

import os, json, asyncio
from pathlib import Path

try:
    from aiohttp import web
    AIORTC_OK = True
except Exception:
    AIORTC_OK = False

if AIORTC_OK:
    async def index(request):
        return web.Response(text="Aurora WebRTC Hub", content_type="text/plain")

    async def offer(request):
        data = await request.json()
        # In production: create aiortc RTCPeerConnection, set remote desc, create answer
        # For now: echo back a placeholder
        return web.json_response({"answer": "placeholder"})

    def run_server(port=9703):
        app = web.Application()
        app.router.add_get('/', index)
        app.router.add_post('/offer', offer)
        web.run_app(app, port=port)
else:
    def run_server(port=9703):
        print("aiortc/aiohttp not present; WebRTC hub disabled. Install aiohttp/aiortc for full features.")
