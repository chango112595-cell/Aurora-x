#!/usr/bin/env python3
"""
Aurora Chat Server - Enhanced with Aurora Core
==============================================

Simple, focused chat server that uses Aurora Core Intelligence
for all conversation processing. No more complex luminar_nexus dependencies.
"""

import asyncio
import os
import time

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from aurora_core import create_aurora_core

# Global Aurora Core instance
AURORA_CORE = None


def initialize_aurora_core():
    """Initialize Aurora Core Intelligence with orchestration"""
    global AURORA_CORE
    if AURORA_CORE is None:
        print("🧠 Initializing Aurora Core Intelligence...")
        print("🎛️ Loading orchestration capabilities...")
        AURORA_CORE = create_aurora_core()
        print("✅ Aurora Core ready - Intelligence + Orchestration active")
        print("🌟 Luminar Nexus preserved for utilities")
    return AURORA_CORE


# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """Aurora's enhanced chat endpoint using Aurora Core"""
    try:
        # Initialize Aurora Core if needed
        aurora = initialize_aurora_core()

        # Get request data
        data = request.get_json()
        message = data.get("message", "")
        session_id = data.get("session_id", "default")
        reset_session = data.get("reset_session", False)

        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        # Reset session context if requested or if it's a greeting to interface
        if reset_session or (session_id == "cosmic-nexus-ui" and any(greeting in message.lower() for greeting in ["hello", "hi", "hey"])):
            if session_id in aurora.conversation_contexts:
                del aurora.conversation_contexts[session_id]

        # Check if this is a system management request
        msg_lower = message.lower()
        if any(
            cmd in msg_lower
            for cmd in ["start all", "stop all", "fire up", "status", "health", "restart chat", "system"]
        ):
            # Use Aurora's autonomous system management
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(aurora.autonomous_system_management(message))
            loop.close()
        else:
            # Process with Aurora Core Intelligence for conversation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(aurora.process_conversation(message, session_id))
            loop.close()

        return jsonify(
            {
                "response": response,
                "session_id": session_id,
                "timestamp": time.time(),
                "aurora_version": "2.0",
                "core_intelligence": True,
                "orchestration_active": True,
                "luminar_nexus_preserved": True,
            }
        )

    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat/status", methods=["GET"])
def chat_status():
    """Get Aurora chat system status"""
    aurora = initialize_aurora_core()
    status = aurora.get_system_status()

    return jsonify(
        {
            "status": "online",
            "aurora_core_version": status["aurora_core_version"],
            "intelligence_tiers_active": status["intelligence_tiers_active"],
            "autonomous_mode": status["autonomous_mode"],
            "active_conversations": status["active_conversations"],
            "enhanced_nlp": True,
            "server_type": "Aurora Core Chat Server",
        }
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "server": "Aurora Core Chat"})


@app.route("/api/chat/reset", methods=["POST"])
def reset_session():
    """Reset a conversation session"""
    try:
        aurora = initialize_aurora_core()
        data = request.get_json()
        session_id = data.get("session_id", "cosmic-nexus-ui")
        
        # Clear the session context
        if session_id in aurora.conversation_contexts:
            del aurora.conversation_contexts[session_id]
        
        return jsonify({
            "status": "success",
            "message": f"Session {session_id} reset",
            "timestamp": time.time()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/aurora_cosmic_nexus.html")
def serve_cosmic_interface():
    """Serve the Aurora Cosmic Interface"""
    try:
        html_path = os.path.abspath("aurora_cosmic_nexus.html")
        print(f"🌌 Serving HTML from: {html_path}")
        if os.path.exists(html_path):
            return send_file(html_path)
        else:
            print(f"❌ HTML file not found at: {html_path}")
            return "Aurora Cosmic Interface not found", 404
    except Exception as e:
        print(f"❌ Error serving interface: {e}")
        return f"Error loading interface: {str(e)}", 500


@app.route("/", methods=["GET"])
def serve_home():
    """Redirect to Aurora Cosmic Interface"""
    return serve_cosmic_interface()


def run_aurora_chat_server(port=5003):
    """Run Aurora's enhanced chat server"""
    print(f"🌌 Aurora Core Chat Server starting on port {port}...")
    print("🧠 Using Aurora Core Intelligence v2.0")
    print("⚡ Enhanced natural language processing active")
    print("🚀 Ready for intelligent conversations!\n")

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5003
    run_aurora_chat_server(port)
