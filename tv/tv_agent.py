#!/usr/bin/env python3
"""
TV agent exposes a small REST API for TV apps to fetch wallboard and commands
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            self.send_response(200); self.end_headers()
            self.wfile.write(json.dumps({"status":"ok"}).encode())
        else:
            self.send_response(404); self.end_headers()

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 9802), H).serve_forever()
