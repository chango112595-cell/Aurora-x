#!/usr/bin/env python3
"""
Aurora Chat Server - Integrated with Luminar Nexus V2
=====================================================

Chat server that properly routes through Luminar Nexus V2's
AI-driven orchestration layer to Aurora Core Intelligence.

Architecture: UI → Nexus V2 (Guardian/Manager) → Aurora Core (Intelligence)
"""

import asyncio
import os
import sys
import time

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from aurora_core import create_aurora_core

# Add tools directory for Luminar Nexus V2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tools"))

try:
    from luminar_nexus_v2 import LuminarNexusV2

    NEXUS_V2_AVAILABLE = True
except ImportError:
    LuminarNexusV2 = None
    NEXUS_V2_AVAILABLE = False
    print("[WARN] Luminar Nexus V2 not available - falling back to direct Aurora Core")


# Global instances
_aurora_core = None
_nexus_v2 = None


def initialize_aurora_system():
    """Initialize complete Aurora system with Nexus V2 orchestration"""
    global _aurora_core, _nexus_v2

    if _aurora_core is None:
        print("🧠 Initializing Aurora Core Intelligence...")
        _aurora_core = create_aurora_core()
        print("✅ Aurora Core Intelligence ready")

    if NEXUS_V2_AVAILABLE and _nexus_v2 is None:
        print("🌌 Initializing Luminar Nexus V2 Orchestrator...")
        _nexus_v2 = LuminarNexusV2()
        print("✅ Nexus V2 orchestration layer active")
        print("   • AI-driven service management")
        print("   • Security Guardian enabled")
        print("   • Quantum coherence monitoring")

    return _aurora_core, _nexus_v2


# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """
    Aurora's chat endpoint - Routes through Nexus V2 orchestration
    Architecture: Request → Nexus V2 Security/AI Layer → Aurora Core → Response
    """
    try:
        # Initialize Aurora system with Nexus V2
        aurora, nexus = initialize_aurora_system()

        # Get request data
        data = request.get_json()
        message = data.get("message", "")
        session_id = data.get("session_id", "default")
        should_reset = data.get("reset_session", False)

        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Session isolation - always reset on page load (cosmic-nexus-ui greeting detection)
        if should_reset or (
            session_id == "cosmic-nexus-ui" and any(
                greeting in message.lower() for greeting in ["hello", "hi", "hey"])
        ):
            if session_id in aurora.conversation_contexts:
                print(f"🔄 Session reset: {session_id}")
                del aurora.conversation_contexts[session_id]

        # NEXUS V2 ROUTING: Security check and AI orchestration
        if nexus:
            # Security Guardian: Threat detection
            request_data = {
                "ip": request.remote_addr,
                "path": request.path,
                "body": data,
            }
            threats = nexus.security_guardian.detect_threats(request_data)
            if threats:
                print(f"🛡️ Security Guardian blocked: {threats}")
                return jsonify({"error": "Security threat detected", "threats": threats}), 403

            # AI Orchestrator: Optimize routing based on load
            if nexus.config.get("ai_learning_enabled"):
                # Learn from response if method exists
                if hasattr(nexus.ai_orchestrator, 'learn_from_response'):
                    nexus.ai_orchestrator.learn_from_response(
                        message, time.time(), 1.0)

        # Check if this is a system management request
        msg_lower = message.lower()
        if any(
            cmd in msg_lower
            for cmd in [
                "start all",
                "stop all",
                "fire up",
                "status",
                "health",
                "restart chat",
                "system",
            ]
        ):
            # Use Aurora's autonomous system management
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                aurora.autonomous_system_management(message))
            loop.close()
        else:
            # Process with Aurora Core Intelligence for conversation
            # PRIORITY FIX: Pass fresh context to avoid "collaborative" tone
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                aurora.process_conversation(message, session_id))
            loop.close()

        return jsonify(
            {
                "response": response,
                "session_id": session_id,
                "timestamp": time.time(),
                "aurora_version": "2.0",
                "nexus_version": nexus.version if nexus else "N/A",
                "quantum_coherence": nexus.quantum_mesh.coherence_level if nexus else None,
                "security_guardian_active": True if nexus else False,
                "ai_orchestration_active": True if nexus else False,
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

        return jsonify(
            {
                "status": "success",
                "message": f"Session {session_id} reset",
                "timestamp": time.time(),
            }
        )
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


def run_aurora_chat_server(port=9000):
    """Run Aurora's enhanced chat server"""
    print(f"🌌 Aurora Core Chat Server starting on port {port}...")
    print("🧠 Using Aurora Core Intelligence v2.0")
    print("⚡ Enhanced natural language processing active")
    print("🚀 Ready for intelligent conversations!\n")

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    import argparse
    import sys

    # Set UTF-8 encoding for Windows compatibility
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    parser = argparse.ArgumentParser(description="Aurora Chat Server")
    parser.add_argument("--port", type=int, default=9000,
                        help="Port to run the server on")
    args = parser.parse_args()

    run_aurora_chat_server(args.port)
