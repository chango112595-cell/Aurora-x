#!/usr/bin/env python3
"""
WebRTC Hub - Real Implementation
- Uses aiortc for WebRTC peer connections when available
- Provides proper error responses when dependencies missing
- Handles signaling for offer/answer exchange
"""

import os
import json
import asyncio
import logging
from pathlib import Path

_logger = logging.getLogger("aurora.webrtc_hub")

# Check for required dependencies
AIORTC_OK = False
AIOHTTP_OK = False

try:
    from aiohttp import web
    AIOHTTP_OK = True
except ImportError:
    _logger.warning("aiohttp not installed - WebRTC signaling unavailable")

try:
    from aiortc import RTCPeerConnection, RTCSessionDescription
    AIORTC_OK = True
except ImportError:
    _logger.info("aiortc not installed - using signaling-only mode")

# Store active peer connections
_peer_connections: dict = {}


if AIOHTTP_OK:
    async def index(request):
        """Health check endpoint"""
        return web.Response(
            text=json.dumps({
                "service": "Aurora WebRTC Hub",
                "aiortc_available": AIORTC_OK,
                "status": "ready" if AIORTC_OK else "signaling_only"
            }),
            content_type="application/json"
        )

    async def offer(request):
        """Handle WebRTC offer and return answer"""
        try:
            data = await request.json()

            if not AIORTC_OK:
                # Without aiortc, we can only do signaling relay
                _logger.warning(
                    "WebRTC offer received but aiortc not available")
                return web.json_response({
                    "error": "WebRTC unavailable",
                    "reason": "aiortc not installed",
                    "hint": "Install aiortc for full WebRTC support: pip install aiortc"
                }, status=503)

            # Parse the incoming offer
            offer_sdp = data.get("sdp")
            offer_type = data.get("type", "offer")

            if not offer_sdp:
                return web.json_response({
                    "error": "Missing SDP in offer"
                }, status=400)

            # Create peer connection
            pc = RTCPeerConnection()
            pc_id = str(id(pc))
            _peer_connections[pc_id] = pc

            @pc.on("connectionstatechange")
            async def on_connection_state_change():
                _logger.info(f"Connection state: {pc.connectionState}")
                if pc.connectionState in ["failed", "closed"]:
                    _peer_connections.pop(pc_id, None)

            # Set remote description (the offer)
            offer_desc = RTCSessionDescription(sdp=offer_sdp, type=offer_type)
            await pc.setRemoteDescription(offer_desc)

            # Create and set local description (the answer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            return web.json_response({
                "type": pc.localDescription.type,
                "sdp": pc.localDescription.sdp,
                "connection_id": pc_id
            })

        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            _logger.error(f"Error handling offer: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def close_connection(request):
        """Close a peer connection"""
        try:
            data = await request.json()
            pc_id = data.get("connection_id")

            if pc_id and pc_id in _peer_connections:
                pc = _peer_connections.pop(pc_id)
                await pc.close()
                return web.json_response({"status": "closed"})

            return web.json_response({"error": "Connection not found"}, status=404)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    def run_server(port=9703):
        """Start the WebRTC signaling server"""
        app = web.Application()
        app.router.add_get('/', index)
        app.router.add_post('/offer', offer)
        app.router.add_post('/close', close_connection)

        _logger.info(f"Starting WebRTC Hub on port {port}")
        _logger.info(f"aiortc available: {AIORTC_OK}")

        web.run_app(app, port=port)

else:
    def run_server(port=9703):
        """Placeholder when aiohttp not available"""
        print("ERROR: aiohttp not installed. WebRTC Hub requires aiohttp.")
        print("Install with: pip install aiohttp")
        print("For full WebRTC support also install: pip install aiortc")
        raise SystemExit(1)
