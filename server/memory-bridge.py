#!/usr/bin/env python3
"""
Aurora Memory Bridge Service
Exposes Memory Manager functionality via HTTP API for TypeScript integration
"""

import sys
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.memory_manager import AuroraMemoryManager

# Global memory instance
memory = AuroraMemoryManager(base="data/memory")


class MemoryBridgeHandler(BaseHTTPRequestHandler):
    """HTTP handler for memory operations"""

    def do_POST(self):
        """Handle POST requests for memory operations"""
        try:
            path = urlparse(self.path).path
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}

            if path == '/memory/write':
                # Write to memory
                text = data.get('text', '')
                meta = data.get('meta', {})
                longterm = data.get('longterm', False)

                # Store message in memory
                memory.save_message("user", text)
                
                # Store as a fact with metadata
                import uuid
                import datetime
                mem_id = str(uuid.uuid4())
                
                # Create enriched fact entry
                fact_data = {
                    "text": text,
                    "meta": meta,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "longterm" if longterm else "shortterm"
                }
                memory.remember_fact(f"memory_{mem_id}", fact_data)
                
                # Log the event
                memory.log_event("memory_write", {
                    "id": mem_id,
                    "text_length": len(text),
                    "has_meta": bool(meta),
                    "longterm": longterm
                })

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'id': mem_id,
                    'longterm': longterm
                }).encode())

            elif path == '/memory/query':
                # Query memory
                query_text = data.get('query', '')
                top_k = data.get('top_k', 5)

                # Search through facts for matching memories
                serializable_results = []
                query_lower = query_text.lower()
                
                # Search through all facts
                for key, fact_data in memory.facts.items():
                    if key.startswith('memory_'):
                        fact_value = fact_data.get('value', {})
                        if isinstance(fact_value, dict):
                            text = fact_value.get('text', '')
                            if query_lower in text.lower():
                                serializable_results.append({
                                    'id': key.replace('memory_', ''),
                                    'text': text,
                                    'meta': fact_value.get('meta', {}),
                                    'score': 0.95,
                                    'timestamp': fact_value.get('timestamp', fact_data.get('stored_at', ''))
                                })
                
                # Also try semantic recall as fallback
                if not serializable_results:
                    semantic_result = memory.recall_semantic(query_text)
                    if semantic_result:
                        import uuid
                        import datetime
                        serializable_results.append({
                            'id': str(uuid.uuid4()),
                            'text': semantic_result,
                            'meta': {},
                            'score': 0.8,
                            'timestamp': datetime.datetime.now().isoformat()
                        })
                
                # Search through recent short-term messages
                for msg in memory.short_term[-top_k:]:
                    if query_lower in msg.get('content', '').lower():
                        import uuid
                        serializable_results.append({
                            'id': str(uuid.uuid4()),
                            'text': msg.get('content', ''),
                            'meta': {'role': msg.get('role', 'unknown')},
                            'score': 0.7,
                            'timestamp': msg.get('timestamp', '')
                        })
                
                # Sort by score and limit results
                serializable_results.sort(key=lambda x: x['score'], reverse=True)
                serializable_results = serializable_results[:top_k]

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'results': serializable_results
                }).encode())

            else:
                self.send_error(404, 'Endpoint not found')

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())

    def do_GET(self):
        """Handle GET requests for status"""
        if self.path == '/memory/status':
            stats = memory.get_memory_stats()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'status': {
                    'short_term_count': stats['short_term_count'],
                    'long_term_count': stats['long_term_count'],
                    'total_entries': stats['short_term_count'] + stats['long_term_count'] + stats['facts_count']
                }
            }).encode())
        else:
            self.send_error(404, 'Endpoint not found')

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def start_memory_service(port=5003):
    """Start the memory bridge HTTP server"""
    server = HTTPServer(('127.0.0.1', port), MemoryBridgeHandler)
    print(f"[MEMORY BRIDGE] Running on http://127.0.0.1:{port}", flush=True)
    print("[MEMORY BRIDGE] Ready for memory operations", flush=True)
    server.serve_forever()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5003
    start_memory_service(port)
