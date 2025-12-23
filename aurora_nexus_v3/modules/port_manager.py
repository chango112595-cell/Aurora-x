"""
Port Manager - Universal port management
Registry, lifecycle, auto-detection, NAT traversal
"""

import asyncio
import socket
import time
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
import threading


class PortState(Enum):
    FREE = "free"
    RESERVED = "reserved"
    ALLOCATED = "allocated"
    IN_USE = "in_use"
    RELEASED = "released"


class PortProtocol(Enum):
    TCP = "tcp"
    UDP = "udp"
    BOTH = "both"


@dataclass
class PortAllocation:
    port: int
    owner: str
    protocol: PortProtocol = PortProtocol.TCP
    state: PortState = PortState.RESERVED
    service_name: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)


class PortManager:
    """
    Universal port management system
    Handles allocation, lifecycle, conflict prevention, NAT traversal
    """
    
    PORT_RANGES = {
        "system": (1, 1023),
        "registered": (1024, 49151),
        "dynamic": (49152, 65535),
        "aurora": (5001, 5999)  # Starts at 5001, 5000 reserved for main app
    }
    
    RESERVED_PORTS = {22, 80, 443, 3306, 5000, 5432, 6379, 27017}  # 5000 reserved for main app
    
    def __init__(self, core):
        self.core = core
        self.logger = core.logger.getChild("ports")
        self.allocations: Dict[int, PortAllocation] = {}
        self.pools: Dict[str, Set[int]] = {}
        self._lock = threading.Lock()
        self._scanner_task: Optional[asyncio.Task] = None
        
        self._init_pools()
    
    def _init_pools(self):
        self.pools["aurora"] = set(range(5001, 5100))  # Starts at 5001, 5000 reserved for main app
        self.pools["services"] = set(range(8000, 9000))
        self.pools["dynamic"] = set(range(49152, 50000))
    
    async def initialize(self):
        self.logger.info("Port manager initialized")
        self.logger.info(f"Aurora port range: {self.PORT_RANGES['aurora']}")
        self._scanner_task = asyncio.create_task(self._scan_loop())
    
    async def shutdown(self):
        """Cleanup port manager - cancel tasks and release allocations."""
        self.logger.info("Port manager shutting down")
        if self._scanner_task:
            self._scanner_task.cancel()
            try:
                await self._scanner_task
            except asyncio.CancelledError:
                self.logger.debug("Scanner task cancellation acknowledged")
            self.logger.debug("Scanner task cancelled")
        with self._lock:
            allocation_count = len(self.allocations)
            self.allocations.clear()
            self._init_pools()
        self.logger.debug(f"Released {allocation_count} port allocations, pools reset")
        self.logger.info("Port manager shut down")
    
    async def _scan_loop(self):
        while True:
            try:
                await asyncio.sleep(60)
                await self._verify_allocations()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Port scan error: {e}")
    
    async def _verify_allocations(self):
        stale = []
        now = time.time()
        
        with self._lock:
            for port, alloc in self.allocations.items():
                if alloc.state == PortState.IN_USE:
                    if not await self._is_port_in_use(port):
                        stale.append(port)
                elif now - alloc.last_used > 3600:
                    stale.append(port)
        
        for port in stale:
            await self.release(port)
    
    async def _is_port_in_use(self, port: int, protocol: PortProtocol = PortProtocol.TCP) -> bool:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM if protocol == PortProtocol.TCP else socket.SOCK_DGRAM
        )
        try:
            sock.settimeout(1)
            sock.bind(("127.0.0.1", port))
            sock.close()
            return False
        except OSError:
            return True
        finally:
            try:
                sock.close()
            except Exception as exc:
                self.logger.debug(f"Failed to close socket for port {port}: {exc}")
    
    async def allocate(
        self,
        owner: str,
        port: Optional[int] = None,
        protocol: PortProtocol = PortProtocol.TCP,
        service_name: Optional[str] = None,
        pool: str = "aurora"
    ) -> Optional[int]:
        with self._lock:
            if port is not None:
                if port in self.allocations:
                    self.logger.warning(f"Port {port} already allocated")
                    return None
                
                if port in self.RESERVED_PORTS:
                    self.logger.warning(f"Port {port} is reserved")
                    return None
                
                if await self._is_port_in_use(port, protocol):
                    self.logger.warning(f"Port {port} is in use")
                    return None
                
                allocated_port = port
            else:
                allocated_port = await self._find_free_port(pool, protocol)
                if allocated_port is None:
                    self.logger.warning(f"No free ports in pool {pool}")
                    return None
            
            allocation = PortAllocation(
                port=allocated_port,
                owner=owner,
                protocol=protocol,
                state=PortState.ALLOCATED,
                service_name=service_name
            )
            
            self.allocations[allocated_port] = allocation
            
            if pool in self.pools and allocated_port in self.pools[pool]:
                self.pools[pool].discard(allocated_port)
            
            self.logger.info(f"Port {allocated_port} allocated to {owner}")
            return allocated_port
    
    async def _find_free_port(self, pool: str, protocol: PortProtocol) -> Optional[int]:
        if pool not in self.pools:
            return None
        
        for port in sorted(self.pools[pool]):
            if port not in self.allocations and not await self._is_port_in_use(port, protocol):
                return port
        
        return None
    
    async def release(self, port: int) -> bool:
        with self._lock:
            if port not in self.allocations:
                return False
            
            alloc = self.allocations.pop(port)
            
            for pool_name, pool_ports in self.pools.items():
                start, end = self.PORT_RANGES.get(pool_name, (0, 0))
                if start <= port <= end:
                    pool_ports.add(port)
                    break
            
            self.logger.info(f"Port {port} released from {alloc.owner}")
            return True
    
    async def mark_in_use(self, port: int) -> bool:
        with self._lock:
            if port in self.allocations:
                self.allocations[port].state = PortState.IN_USE
                self.allocations[port].last_used = time.time()
                return True
        return False
    
    async def get_allocation(self, port: int) -> Optional[Dict[str, Any]]:
        with self._lock:
            if port in self.allocations:
                alloc = self.allocations[port]
                return {
                    "port": alloc.port,
                    "owner": alloc.owner,
                    "protocol": alloc.protocol.value,
                    "state": alloc.state.value,
                    "service_name": alloc.service_name,
                    "age_seconds": time.time() - alloc.created_at
                }
        return None
    
    async def get_all_allocations(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {
                    "port": a.port,
                    "owner": a.owner,
                    "protocol": a.protocol.value,
                    "state": a.state.value,
                    "service_name": a.service_name
                }
                for a in self.allocations.values()
            ]
    
    async def scan_range(
        self,
        start: int,
        end: int,
        protocol: PortProtocol = PortProtocol.TCP
    ) -> List[int]:
        in_use = []
        for port in range(start, min(end + 1, start + 100)):
            if await self._is_port_in_use(port, protocol):
                in_use.append(port)
        return in_use
    
    async def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total_allocated = len(self.allocations)
            in_use = sum(1 for a in self.allocations.values() if a.state == PortState.IN_USE)
            
            pool_stats = {}
            for pool_name, pool_ports in self.pools.items():
                pool_stats[pool_name] = {
                    "available": len(pool_ports),
                    "allocated": sum(1 for p in self.allocations if p in range(
                        self.PORT_RANGES.get(pool_name, (0, 0))[0],
                        self.PORT_RANGES.get(pool_name, (0, 0))[1] + 1
                    ))
                }
        
        return {
            "total_allocated": total_allocated,
            "in_use": in_use,
            "pools": pool_stats
        }
