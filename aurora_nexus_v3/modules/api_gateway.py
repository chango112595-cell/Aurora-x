"""
API Gateway - Universal API access
REST, WebSocket, GraphQL support with rate limiting and auth
"""

import asyncio
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any


class APIProtocol(Enum):
    REST = "rest"
    WEBSOCKET = "websocket"
    GRAPHQL = "graphql"
    GRPC = "grpc"


@dataclass
class APIEndpoint:
    path: str
    method: str
    handler: Callable
    protocol: APIProtocol = APIProtocol.REST
    auth_required: bool = False
    rate_limit: int | None = None
    description: str = ""


@dataclass
class RateLimitEntry:
    count: int = 0
    reset_at: float = 0


class APIGateway:
    """
    Universal API gateway with routing, auth, and rate limiting
    Supports REST, WebSocket, GraphQL protocols
    """

    def __init__(self, core):
        self.core = core
        self.logger = core.logger.getChild("api")
        self.endpoints: dict[str, APIEndpoint] = {}
        self.middleware: list[Callable] = []
        self.rate_limits: dict[str, RateLimitEntry] = {}
        self._lock = threading.Lock()
        self._stats = {"requests": 0, "errors": 0, "rate_limited": 0}

        self._register_core_endpoints()

    async def initialize(self):
        self.logger.info("API gateway initialized")
        self.logger.info(f"Registered {len(self.endpoints)} endpoints")

    async def shutdown(self):
        """Cleanup API gateway resources."""
        self.logger.info("API gateway shutting down")
        with self._lock:
            endpoint_count = len(self.endpoints)
            self.endpoints.clear()
            self.middleware.clear()
            self.rate_limits.clear()
        self.logger.debug(f"Cleared {endpoint_count} endpoints, middleware, and rate limits")
        self.logger.info("API gateway shut down")

    def _register_core_endpoints(self):
        self.register("GET", "/api/health", self._health_handler, description="Health check")
        self.register("GET", "/api/status", self._status_handler, description="System status")
        self.register("GET", "/api/modules", self._modules_handler, description="List modules")
        self.register("GET", "/api/services", self._services_handler, description="List services")
        self.register("GET", "/api/ports", self._ports_handler, description="List port allocations")
        self.register(
            "GET", "/api/resources", self._resources_handler, description="Resource usage"
        )
        self.register("GET", "/api/hardware", self._hardware_handler, description="Hardware info")

    def register(
        self,
        method: str,
        path: str,
        handler: Callable,
        protocol: APIProtocol = APIProtocol.REST,
        auth_required: bool = False,
        rate_limit: int | None = None,
        description: str = "",
    ):
        key = f"{method}:{path}"
        self.endpoints[key] = APIEndpoint(
            path=path,
            method=method,
            handler=handler,
            protocol=protocol,
            auth_required=auth_required,
            rate_limit=rate_limit,
            description=description,
        )
        self.logger.debug(f"Registered endpoint: {method} {path}")

    def add_middleware(self, middleware: Callable):
        self.middleware.append(middleware)

    async def handle_request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        client_id: str | None = None,
    ) -> dict[str, Any]:
        self._stats["requests"] += 1
        start_time = time.time()

        key = f"{method}:{path}"

        if key not in self.endpoints:
            self._stats["errors"] += 1
            return self._error_response(404, "Endpoint not found")

        endpoint = self.endpoints[key]

        if endpoint.rate_limit and client_id:
            if not self._check_rate_limit(client_id, endpoint.rate_limit):
                self._stats["rate_limited"] += 1
                return self._error_response(429, "Rate limit exceeded")

        if endpoint.auth_required:
            if not await self._check_auth(headers):
                return self._error_response(401, "Unauthorized")

        for mw in self.middleware:
            try:
                result = (
                    await mw(method, path, body, headers)
                    if asyncio.iscoroutinefunction(mw)
                    else mw(method, path, body, headers)
                )
                if result is not None:
                    return result
            except Exception as e:
                self.logger.error(f"Middleware error: {e}")

        try:
            if asyncio.iscoroutinefunction(endpoint.handler):
                result = await endpoint.handler(body, headers)
            else:
                result = endpoint.handler(body, headers)

            return {
                "success": True,
                "data": result,
                "meta": {
                    "duration_ms": (time.time() - start_time) * 1000,
                    "path": path,
                    "method": method,
                },
            }

        except Exception as e:
            self._stats["errors"] += 1
            self.logger.error(f"Handler error for {key}: {e}")
            return self._error_response(500, str(e))

    def _check_rate_limit(self, client_id: str, limit: int) -> bool:
        now = time.time()

        with self._lock:
            if client_id not in self.rate_limits:
                self.rate_limits[client_id] = RateLimitEntry(count=1, reset_at=now + 60)
                return True

            entry = self.rate_limits[client_id]

            if now > entry.reset_at:
                entry.count = 1
                entry.reset_at = now + 60
                return True

            if entry.count >= limit:
                return False

            entry.count += 1
            return True

    async def _check_auth(self, headers: dict[str, str] | None) -> bool:
        if not headers:
            return False

        api_key = headers.get("x-api-key") or headers.get("authorization", "").replace(
            "Bearer ", ""
        )

        if not api_key:
            return False

        expected_key = self.core.config.security.api_key
        return api_key == expected_key if expected_key else True

    def _error_response(self, status: int, message: str) -> dict[str, Any]:
        return {"success": False, "error": {"status": status, "message": message}}

    async def _health_handler(self, body, headers):
        return await self.core.health_check()

    async def _status_handler(self, body, headers):
        return self.core.get_status()

    async def _modules_handler(self, body, headers):
        return {
            "modules": [
                {"name": name, "loaded": status.loaded, "healthy": status.healthy}
                for name, status in self.core.module_status.items()
            ]
        }

    async def _services_handler(self, body, headers):
        registry = await self.core.get_module("service_registry")
        if registry:
            return {"services": await registry.get_all()}
        return {"services": []}

    async def _ports_handler(self, body, headers):
        port_mgr = await self.core.get_module("port_manager")
        if port_mgr:
            return {
                "allocations": await port_mgr.get_all_allocations(),
                "stats": await port_mgr.get_stats(),
            }
        return {"allocations": [], "stats": {}}

    async def _resources_handler(self, body, headers):
        resource_mgr = await self.core.get_module("resource_manager")
        if resource_mgr:
            return {
                "usage": await resource_mgr.get_usage(),
                "available": await resource_mgr.get_available(),
            }
        return {"usage": {}, "available": {}}

    async def _hardware_handler(self, body, headers):
        hw_detector = await self.core.get_module("hardware_detector")
        if hw_detector:
            return await hw_detector.get_info()
        return {}

    def get_endpoints(self) -> list[dict[str, Any]]:
        return [
            {
                "method": ep.method,
                "path": ep.path,
                "protocol": ep.protocol.value,
                "auth_required": ep.auth_required,
                "rate_limit": ep.rate_limit,
                "description": ep.description,
            }
            for ep in self.endpoints.values()
        ]

    def get_stats(self) -> dict[str, Any]:
        return {
            "endpoints_count": len(self.endpoints),
            "requests_total": self._stats["requests"],
            "errors_total": self._stats["errors"],
            "rate_limited_total": self._stats["rate_limited"],
            "error_rate": self._stats["errors"] / self._stats["requests"]
            if self._stats["requests"] > 0
            else 0,
        }
