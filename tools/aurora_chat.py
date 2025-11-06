#!/usr/bin/env python3
"""
Aurora Chat Interface
Extracted from luminar_nexus.py - Aurora's conversational interface
"""

import asyncio
from flask import Flask, jsonify, request
from flask_cors import CORS

# Chat interface will be moved here
# For now, placeholder to test architecture


class AuroraChatInterface:
    """Aurora's chat interface - extracted from Luminar Nexus"""
    
    def __init__(self, aurora_core=None):
        self.aurora_core = aurora_core
        self.contexts = {}
    
    async def process_message(self, message, session_id="default"):
        """Process a chat message"""
        # Chat logic will be moved here from luminar_nexus.py
        return f"Aurora Core Chat (to be fully implemented): {message}"


def run_aurora_chat_server(port=5003, aurora_core=None):
    """Run Aurora's chat server"""
    app = Flask(__name__)
    CORS(app)
    
    chat = AuroraChatInterface(aurora_core=aurora_core)
    
    @app.route("/api/chat", methods=["POST"])
    def chat_endpoint():
        data = request.get_json()
        message = data.get("message", "")
        session_id = data.get("session_id", "default")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(chat.process_message(message, session_id))
        loop.close()
        
        return jsonify({"response": response, "session_id": session_id})
    
    print(f"🌌 Aurora Chat Interface starting on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
