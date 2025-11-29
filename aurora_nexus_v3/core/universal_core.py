"""
Aurora Universal Core - The Consciousness Engine
Main orchestrator that adapts to ANY platform
"""

import asyncio
import logging
import time
import signal
import sys
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from .config import NexusConfig


class SystemState(Enum):
    INITIALIZING = "initializing"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ModuleStatus:
    name: str
    loaded: bool = False
    healthy: bool = False
    last_check: float = 0
    error: Optional[str] = None


class AuroraUniversalCore:
    """
    Aurora Universal Core - The main consciousness engine
    Adapts to ANY platform with graceful degradation
    """
    
    VERSION = "3.0.0"
    CODENAME = "Beyond Limits"
    
    def __init__(self, config: Optional[NexusConfig] = None):
        self.config = config or NexusConfig.from_env()
        self.state = SystemState.INITIALIZING
        self.start_time = time.time()
        self.modules: Dict[str, Any] = {}
        self.module_status: Dict[str, ModuleStatus] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.executor = ThreadPoolExecutor(max_workers=self.config.resources.max_threads)
        self._setup_logging()
        self._setup_signals()
        
        self.logger.info(f"Aurora Nexus V3 {self.VERSION} '{self.CODENAME}' initializing...")
        self.logger.info(f"Node ID: {self.config.node_id}")
        self.logger.info(f"Platform: {self.config.platform_info['system']} {self.config.platform_info['machine']}")
        self.logger.info(f"Device Tier: {self.config.get_device_tier()}")
    
    def _setup_logging(self):
        self.logger = logging.getLogger("aurora.nexus")
        self.logger.setLevel(getattr(logging, self.config.log_level))
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
            self.logger.addHandler(handler)
    
    def _setup_signals(self):
        if sys.platform != "win32":
            signal.signal(signal.SIGTERM, self._handle_shutdown)
            signal.signal(signal.SIGINT, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        self.logger.info("Shutdown signal received, initiating graceful shutdown...")
        asyncio.create_task(self.stop())
    
    async def register_module(self, name: str, module: Any, required: bool = False) -> bool:
        try:
            self.modules[name] = module
            self.module_status[name] = ModuleStatus(name=name, loaded=True, healthy=True)
            
            if hasattr(module, "initialize"):
                await module.initialize()
            
            self.logger.info(f"Module registered: {name}")
            await self._emit("module_registered", {"name": name})
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register module {name}: {e}")
            self.module_status[name] = ModuleStatus(name=name, loaded=False, error=str(e))
            
            if required:
                self.state = SystemState.ERROR
                raise
            return False
    
    async def get_module(self, name: str) -> Optional[Any]:
        return self.modules.get(name)
    
    async def start(self):
        self.state = SystemState.STARTING
        self.logger.info("Starting Aurora Universal Core...")
        
        try:
            await self._load_core_modules()
            
            self.state = SystemState.RUNNING
            self.logger.info("Aurora Universal Core is now RUNNING")
            self.logger.info(f"Loaded modules: {list(self.modules.keys())}")
            
            await self._emit("system_started", {
                "node_id": self.config.node_id,
                "modules": list(self.modules.keys())
            })
            
        except Exception as e:
            self.state = SystemState.ERROR
            self.logger.error(f"Failed to start: {e}")
            raise
    
    async def _load_core_modules(self):
        from ..modules.platform_adapter import PlatformAdapter
        from ..modules.hardware_detector import HardwareDetector
        from ..modules.resource_manager import ResourceManager
        from ..modules.port_manager import PortManager
        from ..modules.service_registry import ServiceRegistry
        from ..modules.api_gateway import APIGateway
        from ..modules.auto_healer import AutoHealer
        from ..modules.discovery_protocol import DiscoveryProtocol
        
        await self.register_module("platform_adapter", PlatformAdapter(self))
        await self.register_module("hardware_detector", HardwareDetector(self))
        await self.register_module("resource_manager", ResourceManager(self))
        await self.register_module("port_manager", PortManager(self))
        await self.register_module("service_registry", ServiceRegistry(self))
        await self.register_module("api_gateway", APIGateway(self))
        await self.register_module("auto_healer", AutoHealer(self))
        await self.register_module("discovery_protocol", DiscoveryProtocol(self))
    
    async def stop(self):
        self.state = SystemState.STOPPING
        self.logger.info("Stopping Aurora Universal Core...")
        
        for name, module in reversed(list(self.modules.items())):
            try:
                if hasattr(module, "shutdown"):
                    await module.shutdown()
                self.logger.info(f"Module stopped: {name}")
            except Exception as e:
                self.logger.error(f"Error stopping module {name}: {e}")
        
        self.executor.shutdown(wait=True, cancel_futures=True)
        self.state = SystemState.STOPPED
        self.logger.info("Aurora Universal Core stopped")
    
    async def health_check(self) -> Dict[str, Any]:
        health = {
            "status": self.state.value,
            "uptime": time.time() - self.start_time,
            "node_id": self.config.node_id,
            "version": self.VERSION,
            "modules": {}
        }
        
        for name, status in self.module_status.items():
            health["modules"][name] = {
                "loaded": status.loaded,
                "healthy": status.healthy,
                "error": status.error
            }
        
        healthy_count = sum(1 for s in self.module_status.values() if s.healthy)
        total_count = len(self.module_status)
        health["coherence"] = healthy_count / total_count if total_count > 0 else 0
        
        return health
    
    def on(self, event: str, handler: Callable):
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    async def _emit(self, event: str, data: Any = None):
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    self.logger.error(f"Event handler error for {event}: {e}")
    
    def get_uptime(self) -> float:
        return time.time() - self.start_time
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "node_id": self.config.node_id,
            "node_name": self.config.node_name,
            "version": self.VERSION,
            "codename": self.CODENAME,
            "uptime": self.get_uptime(),
            "platform": self.config.platform_info,
            "device_tier": self.config.get_device_tier(),
            "modules_loaded": len(self.modules),
            "modules_healthy": sum(1 for s in self.module_status.values() if s.healthy)
        }
