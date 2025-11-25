#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 5000
HANDLER = http.server.SimpleHTTPRequestHandler

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print(f"🌌 Analysis Document Server Starting...")
print(f"📍 Access at: http://localhost:{PORT}/COMPREHENSIVE_PROJECT_ANALYSIS.html")
print(f"Press Ctrl+C to stop\n")

with socketserver.TCPServer(("0.0.0.0", PORT), HANDLER) as httpd:
    print(f"✅ Server running on port {PORT}...")
    httpd.serve_forever()
