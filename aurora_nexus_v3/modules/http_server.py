"""
HTTP Server - Exposes Aurora Nexus V3 API via HTTP
Allows Express backend to query Nexus status and capabilities
"""

import json
import logging
import threading
import time
from collections import deque
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

activity_log: deque = deque(maxlen=100)
logger = logging.getLogger(__name__)


def log_activity(activity_type: str, message: str, details: dict = None):
    """Log an activity event"""
    entry = {
        "id": f"act_{int(time.time() * 1000)}",
        "timestamp": datetime.now().isoformat(),
        "type": activity_type,
        "message": message,
        "details": details or {},
    }
    activity_log.appendleft(entry)
    return entry


class NexusHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Aurora Nexus V3 API"""

    core = None

    def log_message(self, format_str, *args):
        formatted = format_str % args
        message = f"{self.client_address[0]} - - [{self.log_date_time_string()}] {formatted}"
        if self.core and getattr(self.core, "logger", None):
            self.core.logger.getChild("http_server").debug(message)
        else:
            logger.debug(message)

    def send_json_response(self, data: dict[str, Any], status: int = 200):
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
            self.send_json_response(
                {
                    "status": "healthy",
                    "version": self.core.VERSION,
                    "codename": self.core.CODENAME,
                    "uptime": time.time() - self.core.start_time,
                }
            )

        elif path == "/api/status":
            status = self.core.get_status()
            status["http_server"] = True
            self.send_json_response(status)

        elif path == "/api/modules":
            modules = [
                {"name": name, "loaded": mod_status.loaded, "healthy": mod_status.healthy}
                for name, mod_status in self.core.module_status.items()
            ]
            self.send_json_response({"modules": modules, "count": len(modules)})

        elif path == "/api/workers":
            if not self.core.worker_pool:
                # Return zero workers if pool not initialized
                self.send_json_response(
                    {
                        "total": 0,
                        "active": 0,
                        "idle": 0,
                        "workers": [],
                        "error": "Worker pool not initialized",
                    }
                )
                return
            try:
                pool_status = self.core.worker_pool.get_status()
                workers = self.core.worker_pool.get_all_workers_status()
                self.send_json_response(
                    {
                        "total": pool_status.get("worker_count", 0),
                        "active": pool_status.get("metrics", {}).get("active_workers", 0),
                        "idle": pool_status.get("metrics", {}).get("idle_workers", 0),
                        "workers": workers or [],
                    }
                )
            except Exception as e:
                # Return error but don't fail completely
                self.send_json_response(
                    {
                        "total": 0,
                        "active": 0,
                        "idle": 0,
                        "workers": [],
                        "error": str(e),
                    }
                )

        elif path == "/api/capabilities":
            capabilities = {
                "workers": self.core.WORKER_COUNT,
                "tiers": self.core.TIER_COUNT,
                "aems": self.core.AEM_COUNT,
                "modules": self.core.MODULE_COUNT,
                "hyperspeed_enabled": self.core.hyperspeed_enabled,
                "autonomous_mode": self.core.autonomous_mode,
                "hybrid_mode_enabled": self.core.hybrid_mode_enabled,
            }
            # Add Supervisor status if available
            if self.core.supervisor:
                try:
                    from aurora_nexus_v3.integrations.supervisor_integration import (
                        get_supervisor_status,
                    )

                    supervisor_status = get_supervisor_status()
                    capabilities["supervisor"] = {
                        "connected": True,
                        "healers": supervisor_status.get("healers", 0),
                        "workers": supervisor_status.get("workers", 0),
                        "running": supervisor_status.get("running", False),
                    }
                except Exception:
                    capabilities["supervisor"] = {"connected": False}
            else:
                capabilities["supervisor"] = {"connected": False}

            # Add Luminar V2 status if available
            if self.core.luminar_v2:
                try:
                    from aurora_nexus_v3.integrations.luminar_integration import get_luminar_status

                    luminar_status = get_luminar_status()
                    capabilities["luminar_v2"] = {
                        "connected": True,
                        "version": luminar_status.get("version", "2.0.0"),
                        "quantum_coherence": luminar_status.get("quantum_coherence", 0.0),
                        "services": luminar_status.get("services", 0),
                    }
                except Exception:
                    capabilities["luminar_v2"] = {"connected": False}
            else:
                capabilities["luminar_v2"] = {"connected": False}

            self.send_json_response(capabilities)

        elif path == "/api/supervisor":
            if not self.core.supervisor:
                self.send_json_response({"error": "Supervisor not connected"}, 503)
                return
            try:
                from aurora_nexus_v3.integrations.supervisor_integration import (
                    get_supervisor_status,
                )

                status = get_supervisor_status()
                self.send_json_response(status)
            except Exception as e:
                self.send_json_response({"error": str(e)}, 500)

        elif path == "/api/luminar-v2":
            if not self.core.luminar_v2:
                self.send_json_response({"error": "Luminar V2 not connected"}, 503)
                return
            try:
                from aurora_nexus_v3.integrations.luminar_integration import get_luminar_status

                status = get_luminar_status()
                self.send_json_response(status)
            except Exception as e:
                self.send_json_response({"error": str(e)}, 500)

        elif path == "/api/packs":
            try:
                import os
                import sys

                sys.path.insert(
                    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                )
                from packs import get_pack_summary

                summary = get_pack_summary()
                self.send_json_response(summary)
            except Exception as e:
                self.send_json_response({"error": str(e), "packs": {}}, 500)

        elif path == "/api/manifest":
            manifest_data = {"tiers": 0, "aems": 0, "modules": 0}
            if self.core.manifest_integrator:
                manifest_data = {
                    "tiers": len(getattr(self.core.manifest_integrator, "tiers", [])),
                    "aems": len(getattr(self.core.manifest_integrator, "execution_methods", [])),
                    "modules": len(getattr(self.core.manifest_integrator, "modules", [])),
                }
            # Include aggregated module count if the nexus bridge is attached
            aggregated = 0
            try:
                bridge = getattr(self.core, "nexus_bridge", None)
                if bridge and getattr(bridge, "modules", None):
                    aggregated = len(bridge.modules)
            except Exception:
                aggregated = 0
            manifest_data["aggregated_modules"] = aggregated or manifest_data.get("modules", 0)
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
                    "failed": metrics.tasks_failed,
                }

            self.send_json_response(
                {
                    "activities": list(activity_log),
                    "workers": worker_metrics,
                    "system": {
                        "state": self.core.state.value,
                        "hyperspeed": self.core.hyperspeed_enabled,
                        "autonomous": self.core.autonomous_mode,
                        "hybrid_mode": self.core.hybrid_mode_enabled,
                    },
                    "timestamp": datetime.now().isoformat(),
                }
            )

        elif path == "/api/consciousness":
            worker_pool = self.core.worker_pool
            worker_metrics = None
            if worker_pool:
                metrics = worker_pool.get_metrics()
                worker_metrics = {
                    "total": metrics.total_workers,
                    "active": metrics.active_workers,
                    "idle": metrics.idle_workers,
                    "ready_for_tasks": metrics.idle_workers > 0,
                }

            manifest_state = None
            if self.core.manifest_integrator:
                manifest_state = {
                    "tiers_loaded": len(getattr(self.core.manifest_integrator, "tiers", [])),
                    "aems_loaded": len(getattr(self.core.manifest_integrator, "aems", [])),
                    "modules_loaded": len(getattr(self.core.manifest_integrator, "modules", [])),
                }

            self.send_json_response(
                {
                    "success": True,
                    "consciousness_state": self.core.state.value,
                    "awareness_level": "hyperspeed" if self.core.hyperspeed_enabled else "standard",
                    "autonomous_mode": self.core.autonomous_mode,
                    "hybrid_mode": self.core.hybrid_mode_enabled,
                    "brain_bridge_connected": self.core.brain_bridge is not None,
                    "uptime": time.time() - self.core.start_time,
                    "workers": worker_metrics,
                    "manifest": manifest_state,
                    "peak_capabilities": {
                        "workers": self.core.WORKER_COUNT,
                        "tiers": self.core.TIER_COUNT,
                        "aems": self.core.AEM_COUNT,
                        "modules": self.core.MODULE_COUNT,
                    },
                    "active_goals": [],
                    "recent_cognitive_events": list(activity_log)[:10],
                    "timestamp": datetime.now().isoformat(),
                }
            )

        else:
            self.send_json_response({"error": "Endpoint not found", "path": path}, 404)

    def do_POST(self):
        if self.path == "/api/activity/log":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body) if body else {}

                activity_type = data.get("type", "info")
                message = data.get("message", "Activity logged")
                details = data.get("details", {})

                entry = log_activity(activity_type, message, details)
                self.send_json_response({"success": True, "entry": entry})
            except Exception as e:
                self.send_json_response({"error": str(e)}, 400)

        elif self.path == "/api/cognitive-event":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body) if body else {}

                event_type = data.get("event_type", "cognition")
                source = data.get("source", "aurora-chat")
                message = data.get("message", "")
                context = data.get("context", {})
                importance = data.get("importance", 0.5)

                entry = log_activity(
                    f"cognitive_{event_type}",
                    f"[{source}] {message}",
                    {
                        "context": context,
                        "importance": importance,
                        "source": source,
                        "event_type": event_type,
                    },
                )

                self.send_json_response(
                    {"success": True, "entry": entry, "consciousness_acknowledged": True}
                )
            except Exception as e:
                self.send_json_response({"error": str(e)}, 400)

        elif self.path == "/api/dispatch-task":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body) if body else {}

                task_type = data.get("task_type", "general")
                payload = data.get("payload", {})
                priority = data.get("priority", "normal")

                entry = log_activity(
                    "task_dispatch",
                    f"Task dispatched: {task_type}",
                    {"payload": payload, "priority": priority},
                )

                self.send_json_response(
                    {
                        "success": True,
                        "task_id": entry["id"],
                        "status": "queued",
                        "workers_available": self.core.worker_pool.get_metrics().idle_workers
                        if self.core.worker_pool
                        else 0,
                    }
                )
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
        endpoints = (
            "/api/health, /api/status, /api/modules, /api/capabilities, "
            "/api/packs, /api/manifest, /api/activity"
        )
        self.logger.info(f"Endpoints: {endpoints}")

    def _run_server(self):
        try:
            self.server.serve_forever()
        except Exception as e:
            if self.running:
                self.logger.error(f"HTTP server error: {e}")

    async def shutdown(self):
        """Cleanup HTTP server - stop server thread and release resources."""
        self.logger.info("HTTP server shutting down")
        self.running = False
        if self.server:
            try:
                self.server.shutdown()
                self.logger.debug("HTTP server shutdown complete")
            except Exception as e:
                self.logger.warning(f"Error shutting down HTTP server: {e}")
            self.server = None
        NexusHTTPHandler.core = None
        self.logger.info("HTTP server stopped")

    def get_info(self) -> dict[str, Any]:
        return {
            "port": self.port,
            "running": self.running,
            "endpoints": [
                "/api/health",
                "/api/status",
                "/api/modules",
                "/api/capabilities",
                "/api/packs",
                "/api/manifest",
            ],
        }
