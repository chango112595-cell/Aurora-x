#!/usr/bin/env python3
"""
Aurora Memory Bridge Service
Exposes MemoryMediator functionality via HTTP API for TypeScript integration
"""

import sys
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Add cog_kernel and memory to Python path (must be before cog_kernel imports)
sys.path.insert(0, str(Path(__file__).parent.parent))

from cog_kernel.memory_abstraction.manager import MemoryMediator


# Global memory instance
memory = MemoryMediator()


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

                result = memory.write_event(text, meta, longterm)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'id': result['id'],
                    'longterm': longterm
                }).encode())

            elif path == '/memory/query':
                # Query memory
                query_text = data.get('query', '')
                top_k = data.get('top_k', 5)

                results = memory.query(query_text, top_k)

                # Convert results to JSON-serializable format
                serializable_results = []
                for r in results:
                    serializable_results.append({
                        'id': r['id'],
                        'text': r['text'],
                        'meta': r['meta'],
                        'score': r.get('score', 0)
                    })

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
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'status': 'operational',
                'short_term_count': len(memory.short._index),
                'long_term_count': len(memory.long._index)
            }).encode())
        else:
            self.send_error(404, 'Endpoint not found')

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


import socket


class ReusableHTTPServer(HTTPServer):
    """HTTP server with socket reuse enabled"""
    allow_reuse_address = True
    
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()


def start_memory_service(port=5003):
    """Start the memory bridge HTTP server"""
    try:
        server = ReusableHTTPServer(('127.0.0.1', port), MemoryBridgeHandler)
        print(f"[MEMORY BRIDGE] Running on http://127.0.0.1:{port}", flush=True)
        print("[MEMORY BRIDGE] Ready for memory operations", flush=True)
        server.serve_forever()
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"[MEMORY BRIDGE] Port {port} busy, service may already be running", flush=True)
        else:
            raise


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5003
    start_memory_service(port)
