import http.server
import socketserver
import sys

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

PORT = 5000
print(f"Starting server on port {PORT}...", file=sys.stderr)
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving on port {PORT}", file=sys.stderr, flush=True)
    httpd.serve_forever()
