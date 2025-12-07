"""
HTTP Server - Exposes Aurora Nexus V3 API via HTTP
Allows Express backend to query Nexus status and capabilities
"""

import asyncio
import json
from typing import Any, Dict, List
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from collections import deque
from datetime import datetime


activity_log: deque = deque(maxlen=100)


def log_activity(activity_type: str, message: str, details: Dict = None):
    """Log an activity event"""
    entry = {
        "id": f"act_{int(time.time() * 1000)}",
        "timestamp": datetime.now().isoformat(),
        "type": activity_type,
        "message": message,
        "details": details or {}
    }
    activity_log.appendleft(entry)
    return entry


class NexusHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Aurora Nexus V3 API"""
    
    core = None
    
    def log_message(self, format, *args):
        pass
    
    def send_json_response(self, data: Dict[str, Any], status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        if not self.core:
            self.send_json_response({"error": "Core not initialized"}, 503)
            return
        
        path = self.path.split("?")[0]
        
        if path == "/api/health":
            self.send_json_response({
                "status": "healthy",
                "version": self.core.VERSION,
                "codename": self.core.CODENAME,
                "uptime": time.time() - self.core.start_time
            })
        
        elif path == "/api/status":
            status = self.core.get_status()
            status["http_server"] = True
            self.send_json_response(status)
        
        elif path == "/api/modules":
            modules = [
                {
                    "name": name,
                    "loaded": mod_status.loaded,
                    "healthy": mod_status.healthy
                }
                for name, mod_status in self.core.module_status.items()
            ]
            self.send_json_response({"modules": modules, "count": len(modules)})
        
        elif path == "/api/capabilities":
            self.send_json_response({
                "workers": self.core.WORKER_COUNT,
                "tiers": self.core.TIER_COUNT,
                "aems": self.core.AEM_COUNT,
                "modules": self.core.MODULE_COUNT,
                "hyperspeed_enabled": self.core.hyperspeed_enabled,
                "autonomous_mode": self.core.autonomous_mode,
                "hybrid_mode_enabled": self.core.hybrid_mode_enabled
            })
        
        elif path == "/api/packs":
            try:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                from packs import get_pack_summary
                summary = get_pack_summary()
                self.send_json_response(summary)
            except Exception as e:
                self.send_json_response({"error": str(e), "packs": {}}, 500)
        
        elif path == "/api/manifest":
            manifest_data = {
                "tiers": 0,
                "aems": 0,
                "modules": 0
            }
            if self.core.manifest_integrator:
                manifest_data = {
                    "tiers": len(getattr(self.core.manifest_integrator, 'tiers', [])),
                    "aems": len(getattr(self.core.manifest_integrator, 'aems', [])),
                    "modules": len(getattr(self.core.manifest_integrator, 'modules', []))
                }
            self.send_json_response(manifest_data)
        
        elif path == "/api/activity":
            worker_pool = self.core.worker_pool
            worker_metrics = None
            if worker_pool:
                metrics = worker_pool.get_metrics()
                worker_metrics = {
                    "total": metrics.total_workers,
                    "active": metrics.active_workers,
                    "idle": metrics.idle_workers,
                    "queued": metrics.tasks_queued,
                    "completed": metrics.tasks_completed,
                    "failed": metrics.tasks_failed
                }
            
            self.send_json_response({
                "activities": list(activity_log),
                "workers": worker_metrics,
                "system": {
                    "state": self.core.state.value,
                    "hyperspeed": self.core.hyperspeed_enabled,
                    "autonomous": self.core.autonomous_mode,
                    "hybrid_mode": self.core.hybrid_mode_enabled
                },
                "timestamp": datetime.now().isoformat()
            })
        
        else:
            self.send_json_response({"error": "Endpoint not found", "path": path}, 404)
    
    def do_POST(self):
        if self.path == "/api/activity/log":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}
                
                activity_type = data.get("type", "info")
                message = data.get("message", "Activity logged")
                details = data.get("details", {})
                
                entry = log_activity(activity_type, message, details)
                self.send_json_response({"success": True, "entry": entry})
            except Exception as e:
                self.send_json_response({"error": str(e)}, 400)
        else:
            self.send_json_response({"error": "Endpoint not found"}, 404)


class HTTPServerModule:
    """HTTP server module for Aurora Nexus V3"""
    
    def __init__(self, core, port: int = 5002):
        self.core = core
        self.port = port
        self.server = None
        self.thread = None
        self.logger = core.logger.getChild("http")
        self.running = False
    
    async def initialize(self):
        NexusHTTPHandler.core = self.core
        
        self.running = True
        self.server = HTTPServer(("0.0.0.0", self.port), NexusHTTPHandler)
        
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        
        self.logger.info(f"HTTP server started on port {self.port}")
        self.logger.info(f"Endpoints: /api/health, /api/status, /api/modules, /api/capabilities, /api/packs, /api/manifest, /api/activity")
    
    def _run_server(self):
        try:
            self.server.serve_forever()
        except Exception as e:
            if self.running:
                self.logger.error(f"HTTP server error: {e}")
    
    async def shutdown(self):
        self.running = False
        if self.server:
            self.server.shutdown()
        self.logger.info("HTTP server stopped")
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "port": self.port,
            "running": self.running,
            "endpoints": [
                "/api/health",
                "/api/status", 
                "/api/modules",
                "/api/capabilities",
                "/api/packs",
                "/api/manifest"
            ]
        }
