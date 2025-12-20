#!/usr/bin/env python3
"""
Aurora Chat Server - Flask API Handler with Memory Fabric 2.0 Integration
==========================================================================

A conversational AI chat server that integrates with Aurora's Memory Fabric 2.0
for persistent context, fact storage, and semantic recall.

Features:
- RESTful API for chat interactions
- WebSocket support for real-time messaging
- Memory Fabric 2.0 integration for persistent context
- Multi-project support
- Automatic conversation compression
- Semantic search and recall

Usage:
    python3 aurora_chat_server.py [--port 5003] [--project Aurora-Main]

Author: Aurora AI System
Version: 2.0-enhanced
"""

import os
import sys
import json
import datetime
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.memory_manager import AuroraMemoryManager, get_memory_manager
    MEMORY_FABRIC_AVAILABLE = True
except ImportError:
    try:
        from core.memory_fabric import AuroraMemoryFabric as AuroraMemoryManager, get_memory_fabric as get_memory_manager
        MEMORY_FABRIC_AVAILABLE = True
    except ImportError:
        MEMORY_FABRIC_AVAILABLE = False
        AuroraMemoryManager = None
        get_memory_manager = None
        print("[WARN] Memory Fabric 2.0 not available")

try:
    from aurora_intelligence_manager import AuroraIntelligenceManager
    INTELLIGENCE_AVAILABLE = True
except ImportError:
    INTELLIGENCE_AVAILABLE = False
    AuroraIntelligenceManager = None

app = Flask(__name__)
CORS(app)

memory_instance: Optional[AuroraMemoryManager] = None
intelligence: Optional[Any] = None
current_project: str = "Aurora-Main"


def init_memory(project_name: str = "Aurora-Main") -> Optional[AuroraMemoryManager]:
    """Initialize or get the Memory Fabric instance"""
    global memory_instance, current_project
    
    if not MEMORY_FABRIC_AVAILABLE or not get_memory_manager:
        print("[WARN] Memory Fabric not available")
        return None
    
    try:
        memory_instance = get_memory_manager(base="data/memory")
        memory_instance.set_project(project_name)
        current_project = project_name
        print(f"[Memory Fabric 2.0] Initialized for project: {project_name}")
        return memory_instance
    except Exception as e:
        print(f"[ERROR] Failed to initialize Memory Fabric: {e}")
        return None


def init_intelligence() -> Optional[Any]:
    """Initialize Aurora Intelligence Manager"""
    global intelligence
    
    if not INTELLIGENCE_AVAILABLE:
        return None
    
    try:
        intelligence = AuroraIntelligenceManager()
        intelligence.log("[CHAT] Aurora Chat Server initialized")
        return intelligence
    except Exception as e:
        print(f"[WARN] Intelligence Manager not available: {e}")
        return None


def log_event(event_type: str, data: Dict[str, Any]) -> None:
    """Log an event to Memory Fabric"""
    if memory_instance:
        try:
            memory_instance.log_event(event_type, data)
        except Exception as e:
            print(f"[WARN] Event logging error: {e}")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "aurora-chat-server",
        "memory_fabric": MEMORY_FABRIC_AVAILABLE,
        "project": current_project,
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint with Memory Fabric integration
    
    Request body:
    {
        "message": "Hello Aurora",
        "user_id": "optional_user_id",
        "importance": 0.5
    }
    
    Response:
    {
        "response": "...",
        "context": "...",
        "facts": {...},
        "session_id": "..."
    }
    """
    try:
        data = request.get_json() or {}
        message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        importance = data.get('importance', 0.5)
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        if memory_instance:
            memory_instance.save_message("user", message, importance=importance, tags=[user_id])
        
        context = ""
        if memory_instance:
            context = memory_instance.contextual_recall(message)
        
        response = generate_response(message, context)
        
        if memory_instance:
            memory_instance.save_message("aurora", response, importance=0.6, tags=["response"])
        
        log_event("chat_message", {
            "user_id": user_id,
            "message_length": len(message),
            "response_length": len(response)
        })
        
        result = {
            "response": response,
            "context": context,
            "session_id": memory_instance.session_id if memory_instance else None,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if memory_instance:
            result["facts"] = memory_instance.get_all_facts()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/remember', methods=['POST'])
def remember():
    """
    Store a fact in Memory Fabric
    
    Request body:
    {
        "key": "user_name",
        "value": "Kai",
        "category": "user_info"
    }
    """
    try:
        data = request.get_json() or {}
        key = data.get('key')
        value = data.get('value')
        category = data.get('category', 'general')
        
        if not key or value is None:
            return jsonify({"error": "Key and value are required"}), 400
        
        if memory_instance:
            memory_instance.remember_fact(key, value, category)
            log_event("fact_stored", {"key": key, "category": category})
            return jsonify({
                "status": "stored",
                "key": key,
                "value": value,
                "category": category
            })
        else:
            return jsonify({"error": "Memory Fabric not available"}), 503
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recall', methods=['GET'])
def recall():
    """
    Recall a fact from Memory Fabric
    
    Query params:
    - key: The fact key to recall
    """
    try:
        key = request.args.get('key')
        
        if not key:
            return jsonify({"error": "Key parameter is required"}), 400
        
        if memory_instance:
            value = memory_instance.recall_fact(key)
            if value is not None:
                return jsonify({
                    "key": key,
                    "value": value,
                    "found": True
                })
            else:
                return jsonify({
                    "key": key,
                    "found": False,
                    "message": "Fact not found"
                })
        else:
            return jsonify({"error": "Memory Fabric not available"}), 503
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/facts', methods=['GET'])
def get_facts():
    """Get all stored facts"""
    try:
        if memory_instance:
            facts = memory_instance.get_all_facts()
            return jsonify({
                "facts": facts,
                "count": len(facts)
            })
        else:
            return jsonify({"error": "Memory Fabric not available"}), 503
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/context', methods=['GET'])
def get_context():
    """Get current context summary"""
    try:
        max_tokens = request.args.get('max_tokens', 500, type=int)
        
        if memory_instance:
            context = memory_instance.get_context_summary(max_tokens)
            return jsonify({
                "context": context,
                "project": current_project
            })
        else:
            return jsonify({"error": "Memory Fabric not available"}), 503
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/search', methods=['POST'])
def semantic_search():
    """
    Semantic search through memory
    
    Request body:
    {
        "query": "Python programming",
        "top_k": 5
    }
    """
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        if memory_instance:
            results = memory_instance.recall_semantic(query, top_k)
            serialized = []
            for entry in results:
                serialized.append({
                    "id": entry.id,
                    "content": entry.content,
                    "role": entry.role,
                    "layer": entry.layer,
                    "timestamp": entry.timestamp,
                    "importance": entry.importance
                })
            
            return jsonify({
                "query": query,
                "results": serialized,
                "count": len(serialized)
            })
        else:
            return jsonify({"error": "Memory Fabric not available"}), 503
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get memory system statistics"""
    try:
        if memory_instance:
            stats = memory_instance.get_stats()
            return jsonify(stats)
        else:
            return jsonify({
                "status": "memory_not_available",
                "fabric_version": "2.0-enhanced"
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/project', methods=['POST'])
def set_project():
    """
    Switch to a different project
    
    Request body:
    {
        "project_name": "MyProject"
    }
    """
    try:
        data = request.get_json() or {}
        project_name = data.get('project_name')
        
        if not project_name:
            return jsonify({"error": "project_name is required"}), 400
        
        if memory_instance:
            memory_instance.set_project(project_name)
            global current_project
            current_project = project_name
            
            log_event("project_switched", {"project": project_name})
            
            return jsonify({
                "status": "switched",
                "project": project_name,
                "stats": memory_instance.get_stats()
            })
        else:
            return jsonify({"error": "Memory Fabric not available"}), 503
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/backup', methods=['POST'])
def create_backup():
    """Create a memory backup"""
    try:
        data = request.get_json() or {}
        backup_dir = data.get('backup_dir', 'backups')
        
        if memory_instance:
            backup_path = memory_instance.backup(backup_dir)
            log_event("backup_created", {"path": backup_path})
            
            return jsonify({
                "status": "created",
                "path": backup_path
            })
        else:
            return jsonify({"error": "Memory Fabric not available"}), 503
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/integrity', methods=['GET'])
def verify_integrity():
    """Verify memory file integrity"""
    try:
        if memory_instance:
            hashes = memory_instance.verify_integrity() if hasattr(memory_instance, 'verify_integrity') else memory_instance.integrity_hash()
            return jsonify({
                "status": "verified",
                "files": len(hashes),
                "hashes": hashes
            })
        else:
            return jsonify({"error": "Memory Fabric not available"}), 503
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/conversation/start', methods=['POST'])
def start_conversation():
    """Start a new conversation session"""
    try:
        if memory_instance:
            if hasattr(memory_instance, 'start_conversation'):
                conv_id = memory_instance.start_conversation()
            else:
                memory_instance.clear_session()
                conv_id = memory_instance.session_id
            
            log_event("conversation_started", {"conversation_id": conv_id})
            
            return jsonify({
                "status": "started",
                "conversation_id": conv_id
            })
        else:
            return jsonify({"error": "Memory Fabric not available"}), 503
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def generate_response(message: str, context: str = "") -> str:
    """
    Generate a response to the user message
    
    This is a placeholder for actual AI response generation.
    In production, this should integrate with the local Luminar engine.
    """
    message_lower = message.lower()
    
    if "my name is" in message_lower:
        name = message.split("my name is")[-1].strip().rstrip(".")
        if memory_instance:
            memory_instance.remember_fact("user_name", name)
        return f"Nice to meet you, {name}! I'll remember that."
    
    if "what's my name" in message_lower or "what is my name" in message_lower:
        if memory_instance:
            name = memory_instance.recall_fact("user_name")
            if name:
                return f"Your name is {name}."
        return "I don't know your name yet. What's your name?"
    
    if context:
        return f"Based on my memory: {context}. How can I help you further?"
    
    return "I've received your message and stored it in my memory. How can I assist you?"


def run_chat_server(port: int = 5003, project: str = "Aurora-Main"):
    """Run the Aurora Chat Server"""
    print("=" * 60)
    print("Aurora Chat Server - Memory Fabric 2.0 Enhanced")
    print("=" * 60)
    
    init_memory(project)
    init_intelligence()
    
    if memory_instance:
        memory_instance.save_message("system", "Aurora Chat Server initialized")
        log_event("server_started", {"port": port, "project": project})
    
    print(f"\nStarting server on port {port}...")
    print(f"Project: {project}")
    print(f"Memory Fabric: {'Connected' if MEMORY_FABRIC_AVAILABLE else 'Not Available'}")
    print("\nEndpoints:")
    print(f"  - Health: http://localhost:{port}/health")
    print(f"  - Chat: POST http://localhost:{port}/api/chat")
    print(f"  - Remember: POST http://localhost:{port}/api/remember")
    print(f"  - Recall: GET http://localhost:{port}/api/recall?key=...")
    print(f"  - Facts: GET http://localhost:{port}/api/facts")
    print(f"  - Context: GET http://localhost:{port}/api/context")
    print(f"  - Search: POST http://localhost:{port}/api/search")
    print(f"  - Stats: GET http://localhost:{port}/api/stats")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aurora Chat Server with Memory Fabric 2.0")
    parser.add_argument('--port', type=int, default=5003, help='Port to run the server on')
    parser.add_argument('--project', type=str, default='Aurora-Main', help='Project name for memory compartmentalization')
    
    args = parser.parse_args()
    run_chat_server(port=args.port, project=args.project)
