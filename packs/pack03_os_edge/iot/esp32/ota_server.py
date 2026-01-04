#!/usr/bin/env python3
"""
OTA server for MicroPython ESP32: serves signed update packages.
In production: use secure HTTPS and signed packages verified on device.
"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
import ssl

class Handler(SimpleHTTPRequestHandler):
    pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("OTA server on 8080")
    server.serve_forever()
