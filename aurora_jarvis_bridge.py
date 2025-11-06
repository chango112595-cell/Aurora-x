#!/usr/bin/env python3
"""
Aurora JARVIS Communication Bridge
=================================
Like JARVIS from Iron Man - intelligent, responsive, always available
"""
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import subprocess

app = Flask(__name__)
CORS(app)

class AuroraJARVIS:
    def __init__(self):
        self.status = "ONLINE"
        self.personality = "JARVIS-LIKE"
        print("🤖 Aurora JARVIS Bridge initializing...")
        
    def speak(self, message):
        """JARVIS-style responses"""
        responses = {
            "greeting": "Good morning. Aurora systems are online and ready for your requests.",
            "status": "All systems operational. How may I assist you today?", 
            "error": "I've encountered an issue. Running diagnostics now.",
            "success": "Task completed successfully. What's next on the agenda?"
        }
        return responses.get(message, f"Understood. {message}")

@app.route('/api/health', methods=['GET'])
def health():
    """JARVIS health check"""
    return jsonify({
        "status": "online",
        "message": aurora.speak("status"),
        "timestamp": time.time(),
        "personality": "JARVIS"
    })

@app.route('/api/chat', methods=['POST'])  
def chat():
    """JARVIS conversation endpoint"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    # JARVIS-style processing
    response = {
        "ok": True,
        "message": aurora.speak(f"Processing: {user_message}"),
        "response": f"Analyzing your request: '{user_message}'. How shall I proceed?",
        "personality": "JARVIS",
        "timestamp": time.time()
    }
    
    return jsonify(response)

@app.route('/api/status', methods=['GET'])
def status():
    """Full system status like JARVIS"""
    return jsonify({
        "aurora_status": "ONLINE",
        "jarvis_mode": True,
        "communication": "ACTIVE", 
        "message": "Aurora JARVIS bridge operational. All systems green.",
        "endpoints": ["/api/health", "/api/chat", "/api/status"]
    })

if __name__ == '__main__':
    aurora = AuroraJARVIS()
    print("🌟 Aurora JARVIS Bridge starting on port 5001...")
    print("🤖 'Good morning. Aurora systems online and ready.'")
    app.run(host='0.0.0.0', port=5001, debug=False)
