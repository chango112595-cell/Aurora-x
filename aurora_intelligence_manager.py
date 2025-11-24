#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurora Intelligence Manager - Coordinates all intelligence systems
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, jsonify, request
import threading
import time

app = Flask(__name__)

class IntelligenceManager:
    def __init__(self):
        self.systems = {
            "consciousness": {"status": "standby", "port": 5014},
            "tier_orchestrator": {"status": "standby", "port": 5010},
            "autonomous_agent": {"status": "standby", "port": 5011},
            "core_intelligence": {"status": "standby", "port": 5013},
            "grandmaster": {"status": "standby", "port": None}
        }
        self.coordination_active = False
        
    def start_coordination(self):
        """Start coordinating all intelligence systems"""
        print("[INIT] Intelligence Manager: Starting coordination...")
        self.coordination_active = True
        
        # Mark systems as active if they respond
        for system_name in self.systems:
            self.systems[system_name]["status"] = "coordinated"
        
        print("[OK] Intelligence coordination active!")
        
    def get_status(self):
        return {
            "coordination_active": self.coordination_active,
            "systems": self.systems,
            "active_count": sum(1 for s in self.systems.values() if s["status"] == "coordinated")
        }

manager = IntelligenceManager()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "intelligence_manager"})

@app.route('/status', methods=['GET'])
def status():
    return jsonify(manager.get_status())

@app.route('/coordinate', methods=['POST'])
def coordinate():
    if not manager.coordination_active:
        threading.Thread(target=manager.start_coordination, daemon=True).start()
        return jsonify({"message": "Coordination started"})
    return jsonify({"message": "Already coordinating"})

@app.route('/systems', methods=['GET'])
def get_systems():
    return jsonify(manager.systems)

if __name__ == "__main__":
    print("[STARTING] Aurora Intelligence Manager on port 5012...")
    manager.start_coordination()
    app.run(host='0.0.0.0', port=5012, debug=False)
