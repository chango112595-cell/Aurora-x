#!/usr/bin/env python3
"""
Aurora Memory Fabric v2 HTTP Service
Exposes Memory Fabric v2 functionality via REST API for TypeScript integration
"""

import sys
import os
import json
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from core.memory_fabric import AuroraMemoryFabric, get_memory_fabric

memory: Optional[AuroraMemoryFabric] = None


def get_or_create_memory() -> AuroraMemoryFabric:
    """Get or create the global memory fabric instance"""
    global memory
    if memory is None:
        memory = AuroraMemoryFabric(base="data/memory")
        memory.set_project("Aurora-X")
    return memory


class MemoryFabricHandler(BaseHTTPRequestHandler):
    """HTTP handler for Memory Fabric v2 operations"""

    def send_json(self, data: dict, status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        try:
            mem = get_or_create_memory()
            path = urlparse(self.path).path

            if path == '/status':
                stats = mem.get_stats()
                self.send_json({
                    'success': True,
                    'stats': {
                        'shortTermCount': stats['short_term_count'],
                        'midTermCount': stats['mid_term_count'],
                        'longTermCount': stats['long_term_count'],
                        'semanticCount': stats['semantic_count'],
                        'factCount': stats['fact_count'],
                        'eventCount': stats['event_count'],
                        'totalMemories': stats['short_term_count'] + stats['mid_term_count'] + stats['long_term_count'] + stats['semantic_count'],
                        'activeProject': stats['project'] or 'Aurora-X',
                        'sessionId': stats['session_id'],
                    },
                    'facts': mem.get_all_facts(),
                    'shortTerm': [self._entry_to_dict(e) for e in mem.short_term],
                    'midTerm': [self._entry_to_dict(e) for e in mem.mid_term],
                    'longTerm': [self._entry_to_dict(e) for e in mem.long_term],
                    'semantic': [self._entry_to_dict(e) for e in mem.semantic_memory],
                    'events': mem.event_log[-50:],
                    'conversations': self._get_conversation_list(mem)
                })

            elif path == '/facts':
                facts = mem.get_all_facts()
                self.send_json({
                    'success': True,
                    'facts': facts
                })

            elif path == '/context':
                context = mem.get_context_summary()
                self.send_json({
                    'success': True,
                    'context': context
                })

            elif path == '/integrity':
                hashes = mem.integrity_hash()
                self.send_json({
                    'success': True,
                    'integrity': hashes
                })

            elif path.startswith('/conversation/'):
                conv_id = path.split('/')[-1]
                messages = self._get_conversation_messages(mem, conv_id)
                self.send_json({
                    'success': True,
                    'messages': messages
                })

            else:
                self.send_json({'success': False, 'error': 'Unknown endpoint'}, 404)

        except Exception as e:
            self.send_json({'success': False, 'error': str(e)}, 500)

    def do_POST(self):
        """Handle POST requests"""
        try:
            mem = get_or_create_memory()
            path = urlparse(self.path).path
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}

            if path == '/message':
                role = data.get('role', 'user')
                content = data.get('content', '')
                importance = data.get('importance', 0.5)
                tags = data.get('tags', [])

                if not content:
                    self.send_json({'success': False, 'error': 'Content required'}, 400)
                    return

                entry = mem.save_message(role, content, importance, tags)
                self.send_json({
                    'success': True,
                    'entry': self._entry_to_dict(entry)
                })

            elif path == '/fact':
                key = data.get('key', '')
                value = data.get('value', '')
                category = data.get('category', 'general')

                if not key:
                    self.send_json({'success': False, 'error': 'Key required'}, 400)
                    return

                mem.remember_fact(key, value, category)
                self.send_json({
                    'success': True,
                    'key': key,
                    'value': value,
                    'category': category
                })

            elif path == '/search':
                query = data.get('query', '')
                top_k = data.get('top_k', 5)

                if not query:
                    self.send_json({'success': False, 'error': 'Query required'}, 400)
                    return

                results = mem.recall_semantic(query, top_k)
                self.send_json({
                    'success': True,
                    'results': [self._entry_to_dict(e) for e in results]
                })

            elif path == '/project':
                project_name = data.get('name', '')
                if not project_name:
                    self.send_json({'success': False, 'error': 'Project name required'}, 400)
                    return

                mem.set_project(project_name)
                self.send_json({
                    'success': True,
                    'project': project_name
                })

            elif path == '/conversation/new':
                conv_id = mem.start_conversation()
                self.send_json({
                    'success': True,
                    'conversationId': conv_id
                })

            elif path == '/backup':
                backup_path = mem.backup()
                self.send_json({
                    'success': True,
                    'backupPath': backup_path
                })

            elif path == '/event':
                event_type = data.get('type', 'custom')
                detail = data.get('detail', {})
                mem.log_event(event_type, detail)
                self.send_json({'success': True})

            elif path == '/recall':
                key = data.get('key', '')
                value = mem.recall_fact(key)
                self.send_json({
                    'success': True,
                    'key': key,
                    'value': value
                })

            else:
                self.send_json({'success': False, 'error': 'Unknown endpoint'}, 404)

        except Exception as e:
            self.send_json({'success': False, 'error': str(e)}, 500)

    def _entry_to_dict(self, entry):
        """Convert MemoryEntry to dictionary"""
        return {
            'id': entry.id,
            'content': entry.content,
            'role': entry.role,
            'timestamp': entry.timestamp,
            'layer': entry.layer,
            'importance': entry.importance,
            'tags': entry.tags,
            'metadata': entry.metadata
        }

    def _get_conversation_list(self, mem: AuroraMemoryFabric):
        """Get list of conversation files"""
        conversations = []
        if mem.active_project:
            conv_dir = Path(mem.base) / "projects" / mem.active_project / "conversations"
            if conv_dir.exists():
                for f in conv_dir.glob("*.json"):
                    conversations.append(f.stem)
        return conversations

    def _get_conversation_messages(self, mem: AuroraMemoryFabric, conv_id: str):
        """Get messages from a specific conversation"""
        if mem.active_project:
            conv_file = Path(mem.base) / "projects" / mem.active_project / "conversations" / f"{conv_id}.json"
            if conv_file.exists():
                try:
                    with open(conv_file, 'r') as f:
                        data = json.load(f)
                        return data.get('messages', [])
                except:
                    pass
        return []

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


import socket
import signal
import threading


class ReusableHTTPServer(HTTPServer):
    """HTTP server with socket reuse enabled"""
    allow_reuse_address = True
    
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except OSError:
            return True


def check_existing_service(port: int) -> bool:
    """Check if Memory Fabric service is already responding"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(('127.0.0.1', port))
            s.sendall(b'GET /status HTTP/1.1\r\nHost: localhost\r\n\r\n')
            response = s.recv(1024)
            return b'success' in response.lower() or b'200' in response
    except:
        return False


def start_memory_fabric_service(port: int = 5004):
    """Start the Memory Fabric v2 HTTP server"""
    if check_existing_service(port):
        for _ in range(20):
            time.sleep(0.5)
            if not check_existing_service(port):
                break
        if check_existing_service(port):
            print(f"[MEMORY FABRIC V2] Service already running on port {port}", flush=True)
            return
    
    get_or_create_memory()
    for attempt in range(10):
        try:
            server = ReusableHTTPServer(('127.0.0.1', port), MemoryFabricHandler)
            def _handle_sigterm(signum, frame):
                print("[MEMORY FABRIC V2] Shutdown requested", flush=True)
                threading.Timer(2.0, server.shutdown).start()

            signal.signal(signal.SIGTERM, _handle_sigterm)
            print(f"[MEMORY FABRIC V2] Running on http://127.0.0.1:{port}", flush=True)
            print("[MEMORY FABRIC V2] Ready for operations", flush=True)
            server.serve_forever()
            return
        except OSError as e:
            if 'Address already in use' in str(e) and attempt < 9:
                time.sleep(0.5)
                continue
            if 'Address already in use' in str(e):
                print(f"[MEMORY FABRIC V2] Port {port} busy, assuming service running", flush=True)
                return
            raise


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5004
    start_memory_fabric_service(port)
