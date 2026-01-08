#!/usr/bin/env python3
"""
health_service.py - provides a small local HTTP health endpoint (optional)
If Flask is present, start a tiny health server; otherwise provide a CLI probe.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def probe():
    """Quick composite probe - returns health status."""
    try:
        from .supervisor import Supervisor

        s = Supervisor()
        s.stop()  # stop the monitor thread immediately
        return {"status": "ok", "jobs": s.list_jobs()}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_health_server(port=8099):
    """Optional: run a tiny HTTP health server if flask is available."""
    try:
        from flask import Flask, jsonify

        app = Flask(__name__)

        @app.route("/health")
        def health():
            return jsonify(probe())

        @app.route("/")
        def root():
            return jsonify({"service": "pack04_launcher", "status": "running"})

        app.run(host="0.0.0.0", port=port, threaded=True)
    except ImportError:
        print("Flask not available, health server disabled")
        return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "server":
        run_health_server()
    else:
        print(probe())
