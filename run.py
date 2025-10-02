#!/usr/bin/env python3
"""Simple runner for Aurora-X with status server"""
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class AuroraStatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Aurora-X Ultra Status</title>
                <style>
                    body { font-family: monospace; background: #1a1a1a; color: #0f0; padding: 20px; }
                    h1 { color: #0ff; }
                    pre { background: #000; padding: 10px; border: 1px solid #0f0; }
                    .command { color: #ff0; }
                </style>
            </head>
            <body>
                <h1>🚀 Aurora-X Ultra - Offline Autonomous Coding Engine</h1>
                <p>Status: <strong>ONLINE</strong></p>
                <h2>Usage Examples:</h2>
                <pre>
<span class="command">python -m aurora_x.main --spec-file ./specs/rich_spec.md</span>
    Run synthesis on a specification file

<span class="command">python -m aurora_x.main --dump-corpus "add(a: int, b: int) -> int"</span>
    Query the corpus for similar functions
                </pre>
                <p>Aurora-X is a Python-based offline code synthesis engine.</p>
                <p>Access the command line to run synthesis tasks.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            status = {
                "service": "Aurora-X Ultra",
                "status": "online",
                "version": "0.1.0",
                "milestone": "T02 - Corpus + Seeding"
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress log messages
        pass

print("🚀 Aurora-X Ultra - Starting status server...")
print("=" * 50)
print("Status server running on http://0.0.0.0:5000")
print("\nUsage examples:")
print("  python -m aurora_x.main --spec-file ./specs/rich_spec.md")
print("  python -m aurora_x.main --dump-corpus 'add(a: int, b: int) -> int'")
print("\n✅ Aurora-X is ready!")
print("=" * 50)

# Start HTTP server
server = HTTPServer(('0.0.0.0', 5000), AuroraStatusHandler)
print("\nServer listening on port 5000...")
server.serve_forever()