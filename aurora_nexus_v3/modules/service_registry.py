"""
Service Registry - Universal service catalog
Registration, discovery, health tracking, dependencies
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
import threading


class ServiceState(Enum):
    REGISTERED = "registered"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class ServiceType(Enum):
    API = "api"
    WEBSOCKET = "websocket"
    WORKER = "worker"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    EXTERNAL = "external"
    INTERNAL = "internal"


@dataclass
class ServiceDefinition:
    id: str
    name: str
    type: ServiceType
    host: str = "localhost"
    port: Optional[int] = None
    protocol: str = "http"
    state: ServiceState = ServiceState.REGISTERED
    health_endpoint: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    last_health_check: float = 0
    health_status: bool = True
    failure_count: int = 0


class ServiceRegistry:
    """
    Universal service registry and discovery
    Tracks all services, their health, and dependencies
    """
    
    def __init__(self, core):
        self.core = core
        self.logger = core.logger.getChild("registry")
        self.services: Dict[str, ServiceDefinition] = {}
        self.watchers: Dict[str, List[callable]] = {}
        self._lock = threading.Lock()
        self._health_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        self.logger.info("Service registry initialized")
        self._health_task = asyncio.create_task(self._health_loop())
    
    async def shutdown(self):
        """Cleanup service registry - cancel tasks, clear services and watchers."""
        self.logger.info("Service registry shutting down")
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                self.logger.debug("Health check task cancellation acknowledged")
            self.logger.debug("Health check task cancelled")
        with self._lock:
            service_count = len(self.services)
            self.services.clear()
        watcher_count = len(self.watchers)
        self.watchers.clear()
        self.logger.debug(f"Cleared {service_count} services, {watcher_count} watcher groups")
        self.logger.info("Service registry shut down")
    
    async def _health_loop(self):
        while True:
            try:
                await asyncio.sleep(30)
                await self._check_all_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
    
    async def _check_all_health(self):
        for service_id in list(self.services.keys()):
            try:
                await self.check_health(service_id)
            except Exception as e:
                self.logger.debug(f"Health check failed for {service_id}: {e}")
    
    async def register(
        self,
        name: str,
        service_type: ServiceType,
        host: str = "localhost",
        port: Optional[int] = None,
        protocol: str = "http",
        health_endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None
    ) -> str:
        import uuid
        service_id = str(uuid.uuid4())[:8]
        
        service = ServiceDefinition(
            id=service_id,
            name=name,
            type=service_type,
            host=host,
            port=port,
            protocol=protocol,
            health_endpoint=health_endpoint,
            metadata=metadata or {},
            dependencies=set(dependencies) if dependencies else set()
        )
        
        with self._lock:
            self.services[service_id] = service
        
        self.logger.info(f"Service registered: {name} ({service_id})")
        await self._notify_watchers("registered", service)
        
        return service_id
    
    async def deregister(self, service_id: str) -> bool:
        with self._lock:
            if service_id in self.services:
                service = self.services.pop(service_id)
                self.logger.info(f"Service deregistered: {service.name}")
                await self._notify_watchers("deregistered", service)
                return True
        return False
    
    async def update_state(self, service_id: str, state: ServiceState) -> bool:
        with self._lock:
            if service_id in self.services:
                old_state = self.services[service_id].state
                self.services[service_id].state = state
                self.logger.debug(f"Service {service_id} state: {old_state.value} -> {state.value}")
                await self._notify_watchers("state_changed", self.services[service_id])
                return True
        return False
    
    async def check_health(self, service_id: str) -> bool:
        with self._lock:
            if service_id not in self.services:
                return False
            service = self.services[service_id]
        
        if not service.health_endpoint or not service.port:
            return True
        
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((service.host, service.port))
            sock.close()
            
            healthy = result == 0
            
            with self._lock:
                if service_id in self.services:
                    self.services[service_id].health_status = healthy
                    self.services[service_id].last_health_check = time.time()
                    
                    if not healthy:
                        self.services[service_id].failure_count += 1
                        if self.services[service_id].failure_count >= 3:
                            self.services[service_id].state = ServiceState.FAILED
                    else:
                        self.services[service_id].failure_count = 0
                        if self.services[service_id].state == ServiceState.FAILED:
                            self.services[service_id].state = ServiceState.RUNNING
            
            return healthy
            
        except Exception as e:
            self.logger.debug(f"Health check error for {service_id}: {e}")
            return False
    
    async def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if service_id in self.services:
                return self._service_to_dict(self.services[service_id])
        return None
    
    async def find_by_name(self, name: str) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                self._service_to_dict(s)
                for s in self.services.values()
                if s.name == name
            ]
    
    async def find_by_type(self, service_type: ServiceType) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                self._service_to_dict(s)
                for s in self.services.values()
                if s.type == service_type
            ]
    
    async def get_all(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [self._service_to_dict(s) for s in self.services.values()]
    
    async def get_healthy(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                self._service_to_dict(s)
                for s in self.services.values()
                if s.health_status and s.state == ServiceState.RUNNING
            ]
    
    async def get_dependencies(self, service_id: str) -> List[str]:
        with self._lock:
            if service_id in self.services:
                return list(self.services[service_id].dependencies)
        return []
    
    async def get_dependents(self, service_id: str) -> List[str]:
        with self._lock:
            return [
                s.id for s in self.services.values()
                if service_id in s.dependencies
            ]
    
    def _service_to_dict(self, service: ServiceDefinition) -> Dict[str, Any]:
        return {
            "id": service.id,
            "name": service.name,
            "type": service.type.value,
            "host": service.host,
            "port": service.port,
            "protocol": service.protocol,
            "state": service.state.value,
            "health_status": service.health_status,
            "failure_count": service.failure_count,
            "metadata": service.metadata,
            "dependencies": list(service.dependencies),
            "url": f"{service.protocol}://{service.host}:{service.port}" if service.port else None,
            "age_seconds": time.time() - service.created_at
        }
    
    async def watch(self, event: str, callback: callable):
        if event not in self.watchers:
            self.watchers[event] = []
        self.watchers[event].append(callback)
    
    async def _notify_watchers(self, event: str, service: ServiceDefinition):
        if event in self.watchers:
            for callback in self.watchers[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(service)
                    else:
                        callback(service)
                except Exception as e:
                    self.logger.error(f"Watcher error: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = len(self.services)
            by_state = {}
            by_type = {}
            
            for service in self.services.values():
                state = service.state.value
                by_state[state] = by_state.get(state, 0) + 1
                
                stype = service.type.value
                by_type[stype] = by_type.get(stype, 0) + 1
            
            healthy = sum(1 for s in self.services.values() if s.health_status)
        
        return {
            "total": total,
            "healthy": healthy,
            "unhealthy": total - healthy,
            "by_state": by_state,
            "by_type": by_type,
            "coherence": healthy / total if total > 0 else 1.0
        }
