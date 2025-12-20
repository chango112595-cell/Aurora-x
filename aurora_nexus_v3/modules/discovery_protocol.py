"""
Discovery Protocol - Finds other Aurora instances
mDNS, SSDP, Bluetooth, cloud registry, DHT, mesh networking
"""

import asyncio
import socket
import time
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
import threading

from aurora_nexus_v3.utils.atomic_io import atomic_json_write, load_snapshot


class DiscoveryMethod(Enum):
    MDNS = "mdns"
    SSDP = "ssdp"
    BROADCAST = "broadcast"
    CLOUD = "cloud"
    MANUAL = "manual"


class NodeState(Enum):
    DISCOVERED = "discovered"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    UNREACHABLE = "unreachable"


@dataclass
class DiscoveredNode:
    id: str
    name: str
    host: str
    port: int
    method: DiscoveryMethod
    state: NodeState = NodeState.DISCOVERED
    version: str = "unknown"
    capabilities: List[str] = field(default_factory=list)
    discovered_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    latency_ms: Optional[float] = None


class DiscoveryProtocol:
    """
    Zero-config discovery protocol for Aurora mesh networking
    Finds other Aurora instances on local network and cloud
    """
    
    SERVICE_TYPE = "_aurora._tcp.local."
    BROADCAST_PORT = 5353
    DISCOVERY_INTERVAL = 30
    
    def __init__(self, core):
        self.core = core
        self.logger = core.logger.getChild("discovery")
        self.nodes: Dict[str, DiscoveredNode] = {}
        self.local_node_id = core.config.node_id
        self._lock = threading.Lock()
        self._discovery_task: Optional[asyncio.Task] = None
        self._broadcast_socket: Optional[socket.socket] = None
    
    async def initialize(self):
        self.logger.info("Discovery protocol initialized")
        self._setup_broadcast_socket()
        self._discovery_task = asyncio.create_task(self._discovery_loop())
    
    async def shutdown(self):
        if self._discovery_task:
            self._discovery_task.cancel()
            try:
                await self._discovery_task
            except asyncio.CancelledError:
                pass
        
        if self._broadcast_socket:
            self._broadcast_socket.close()
        
        self.logger.info("Discovery protocol shut down")
    
    def _setup_broadcast_socket(self):
        try:
            self._broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._broadcast_socket.settimeout(1)
            self.logger.debug("Broadcast socket initialized")
        except Exception as e:
            self.logger.warning(f"Failed to setup broadcast socket: {e}")
    
    async def _discovery_loop(self):
        while True:
            try:
                await self._broadcast_presence()
                await self._scan_local_network()
                await self._cleanup_stale_nodes()
                await asyncio.sleep(self.DISCOVERY_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Discovery error: {e}")
                await asyncio.sleep(5)
    
    async def _broadcast_presence(self):
        if not self._broadcast_socket:
            return
        
        announcement = {
            "type": "aurora_announce",
            "node_id": self.local_node_id,
            "name": self.core.config.node_name,
            "port": self.core.config.network.api_port,
            "version": self.core.__class__.VERSION if hasattr(self.core.__class__, 'VERSION') else "3.0.0",
            "capabilities": ["api", "mesh", "discovery"]
        }
        
        try:
            import json
            message = json.dumps(announcement).encode()
            self._broadcast_socket.sendto(message, ('<broadcast>', self.BROADCAST_PORT))
            self.logger.debug("Broadcast presence announcement sent")
        except Exception as e:
            self.logger.debug(f"Broadcast failed: {e}")
    
    async def _scan_local_network(self):
        try:
            local_ip = self._get_local_ip()
            if not local_ip:
                return
            
            network_prefix = ".".join(local_ip.split(".")[:3])
            
            scan_targets = [
                f"{network_prefix}.{i}" for i in range(1, 20)
            ]
            
            for target in scan_targets:
                if target != local_ip:
                    asyncio.create_task(self._probe_host(target))
                    
        except Exception as e:
            self.logger.debug(f"Network scan error: {e}")
    
    async def _probe_host(self, host: str):
        port = self.core.config.network.api_port
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            
            start = time.time()
            result = sock.connect_ex((host, port))
            latency = (time.time() - start) * 1000
            
            sock.close()
            
            if result == 0:
                await self._register_node(host, port, DiscoveryMethod.BROADCAST, latency)
                
        except Exception:
            pass
    
    async def _register_node(
        self,
        host: str,
        port: int,
        method: DiscoveryMethod,
        latency: Optional[float] = None
    ):
        node_key = f"{host}:{port}"
        
        with self._lock:
            if node_key in self.nodes:
                self.nodes[node_key].last_seen = time.time()
                self.nodes[node_key].latency_ms = latency
                self.nodes[node_key].state = NodeState.CONNECTED
            else:
                import uuid
                node = DiscoveredNode(
                    id=str(uuid.uuid4())[:8],
                    name=f"aurora-{host.split('.')[-1]}",
                    host=host,
                    port=port,
                    method=method,
                    latency_ms=latency
                )
                self.nodes[node_key] = node
                self.logger.info(f"Discovered new node: {host}:{port}")
    
    async def _cleanup_stale_nodes(self):
        now = time.time()
        stale_threshold = 120
        
        with self._lock:
            stale = [
                key for key, node in self.nodes.items()
                if now - node.last_seen > stale_threshold
            ]
            
            for key in stale:
                self.nodes[key].state = NodeState.UNREACHABLE
    
    def _get_local_ip(self) -> Optional[str]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            sock.close()
            return ip
        except Exception:
            return None
    
    async def register_manual(self, host: str, port: int, name: Optional[str] = None) -> str:
        import uuid
        node_key = f"{host}:{port}"
        
        node = DiscoveredNode(
            id=str(uuid.uuid4())[:8],
            name=name or f"manual-{host}",
            host=host,
            port=port,
            method=DiscoveryMethod.MANUAL
        )
        
        with self._lock:
            self.nodes[node_key] = node
        
        self.logger.info(f"Manually registered node: {host}:{port}")
        return node.id
    
    async def get_nodes(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {
                    "id": node.id,
                    "name": node.name,
                    "host": node.host,
                    "port": node.port,
                    "method": node.method.value,
                    "state": node.state.value,
                    "version": node.version,
                    "capabilities": node.capabilities,
                    "latency_ms": node.latency_ms,
                    "age_seconds": time.time() - node.discovered_at,
                    "last_seen_seconds": time.time() - node.last_seen
                }
                for node in self.nodes.values()
            ]
    
    async def get_connected(self) -> List[Dict[str, Any]]:
        nodes = await self.get_nodes()
        return [n for n in nodes if n["state"] == "connected"]
    
    async def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = len(self.nodes)
            connected = sum(1 for n in self.nodes.values() if n.state == NodeState.CONNECTED)
            by_method = {}
            
            for node in self.nodes.values():
                method = node.method.value
                by_method[method] = by_method.get(method, 0) + 1
        
        return {
            "total_nodes": total,
            "connected_nodes": connected,
            "local_node_id": self.local_node_id,
            "discovery_methods": by_method,
            "mesh_health": connected / total if total > 0 else 1.0
        }
    
    async def ping_node(self, host: str, port: int) -> Optional[float]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            start = time.time()
            result = sock.connect_ex((host, port))
            latency = (time.time() - start) * 1000
            
            sock.close()
            
            return latency if result == 0 else None
            
        except Exception:
            return None
