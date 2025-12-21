"""
Resource Manager - Smart resource allocation per device
Memory budgeting, CPU throttling, battery awareness
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import threading


class ResourcePriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class ResourceAllocation:
    id: str
    owner: str
    memory_mb: int = 0
    cpu_percent: float = 0
    priority: ResourcePriority = ResourcePriority.NORMAL
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None


@dataclass
class ResourceBudget:
    memory_mb: int
    cpu_percent: float
    max_allocations: int


class ResourceManager:
    """
    Smart resource allocation across the system
    Ensures Aurora never exceeds device limits
    """
    
    def __init__(self, core):
        self.core = core
        self.logger = core.logger.getChild("resources")
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.budgets: Dict[str, ResourceBudget] = {}
        self._lock = threading.Lock()
        self._monitor_task: Optional[asyncio.Task] = None
        
        self._init_budgets()
    
    def _init_budgets(self):
        tier = self.core.config.get_device_tier()
        
        budget_configs = {
            "full": ResourceBudget(memory_mb=2048, cpu_percent=80, max_allocations=500),
            "standard": ResourceBudget(memory_mb=1024, cpu_percent=60, max_allocations=200),
            "lite": ResourceBudget(memory_mb=256, cpu_percent=40, max_allocations=50),
            "micro": ResourceBudget(memory_mb=64, cpu_percent=20, max_allocations=10)
        }
        
        self.total_budget = budget_configs.get(tier, budget_configs["lite"])
    
    async def initialize(self):
        self.logger.info(f"Resource manager initialized with budget: "
                        f"{self.total_budget.memory_mb}MB RAM, "
                        f"{self.total_budget.cpu_percent}% CPU")
        self._monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def shutdown(self):
        """Cleanup resource manager - cancel tasks and release allocations."""
        self.logger.info("Resource manager shutting down")
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self.logger.debug("Monitor task cancelled")
        with self._lock:
            allocation_count = len(self.allocations)
            self.allocations.clear()
            self.budgets.clear()
        self.logger.debug(f"Released {allocation_count} allocations")
        self.logger.info("Resource manager shut down")
    
    async def _monitor_loop(self):
        while True:
            try:
                await asyncio.sleep(30)
                await self._cleanup_expired()
                await self._check_usage()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Resource monitor error: {e}")
    
    async def _cleanup_expired(self):
        now = time.time()
        expired = []
        
        with self._lock:
            for alloc_id, alloc in self.allocations.items():
                if alloc.expires_at and alloc.expires_at < now:
                    expired.append(alloc_id)
            
            for alloc_id in expired:
                del self.allocations[alloc_id]
        
        if expired:
            self.logger.debug(f"Cleaned up {len(expired)} expired allocations")
    
    async def _check_usage(self):
        usage = await self.get_usage()
        
        if usage["memory_percent"] > 90:
            self.logger.warning(f"Memory usage critical: {usage['memory_percent']:.1f}%")
        
        if usage["cpu_percent"] > 90:
            self.logger.warning(f"CPU usage critical: {usage['cpu_percent']:.1f}%")
    
    async def allocate(
        self,
        owner: str,
        memory_mb: int = 0,
        cpu_percent: float = 0,
        priority: ResourcePriority = ResourcePriority.NORMAL,
        ttl_seconds: Optional[int] = None
    ) -> Optional[str]:
        with self._lock:
            current_memory = sum(a.memory_mb for a in self.allocations.values())
            current_cpu = sum(a.cpu_percent for a in self.allocations.values())
            
            if current_memory + memory_mb > self.total_budget.memory_mb:
                self.logger.warning(f"Memory allocation denied for {owner}: "
                                   f"would exceed budget")
                return None
            
            if current_cpu + cpu_percent > self.total_budget.cpu_percent:
                self.logger.warning(f"CPU allocation denied for {owner}: "
                                   f"would exceed budget")
                return None
            
            if len(self.allocations) >= self.total_budget.max_allocations:
                self.logger.warning(f"Max allocations reached, denying {owner}")
                return None
            
            import uuid
            alloc_id = str(uuid.uuid4())[:8]
            
            allocation = ResourceAllocation(
                id=alloc_id,
                owner=owner,
                memory_mb=memory_mb,
                cpu_percent=cpu_percent,
                priority=priority,
                expires_at=time.time() + ttl_seconds if ttl_seconds else None
            )
            
            self.allocations[alloc_id] = allocation
            self.logger.debug(f"Allocated {memory_mb}MB, {cpu_percent}% CPU to {owner}")
            
            return alloc_id
    
    async def release(self, alloc_id: str) -> bool:
        with self._lock:
            if alloc_id in self.allocations:
                alloc = self.allocations.pop(alloc_id)
                self.logger.debug(f"Released allocation {alloc_id} from {alloc.owner}")
                return True
        return False
    
    async def get_usage(self) -> Dict[str, Any]:
        with self._lock:
            total_memory = sum(a.memory_mb for a in self.allocations.values())
            total_cpu = sum(a.cpu_percent for a in self.allocations.values())
        
        return {
            "memory_allocated_mb": total_memory,
            "memory_budget_mb": self.total_budget.memory_mb,
            "memory_percent": (total_memory / self.total_budget.memory_mb * 100) if self.total_budget.memory_mb > 0 else 0,
            "cpu_allocated_percent": total_cpu,
            "cpu_budget_percent": self.total_budget.cpu_percent,
            "cpu_percent": (total_cpu / self.total_budget.cpu_percent * 100) if self.total_budget.cpu_percent > 0 else 0,
            "allocations_count": len(self.allocations),
            "allocations_max": self.total_budget.max_allocations
        }
    
    async def get_allocations(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {
                    "id": a.id,
                    "owner": a.owner,
                    "memory_mb": a.memory_mb,
                    "cpu_percent": a.cpu_percent,
                    "priority": a.priority.name,
                    "age_seconds": time.time() - a.created_at
                }
                for a in self.allocations.values()
            ]
    
    async def set_budget(self, memory_mb: int, cpu_percent: float, max_allocations: int):
        self.total_budget = ResourceBudget(
            memory_mb=memory_mb,
            cpu_percent=cpu_percent,
            max_allocations=max_allocations
        )
        self.logger.info(f"Budget updated: {memory_mb}MB, {cpu_percent}% CPU, "
                        f"max {max_allocations} allocations")
    
    async def get_available(self) -> Dict[str, Any]:
        usage = await self.get_usage()
        return {
            "memory_available_mb": self.total_budget.memory_mb - usage["memory_allocated_mb"],
            "cpu_available_percent": self.total_budget.cpu_percent - usage["cpu_allocated_percent"],
            "allocations_available": self.total_budget.max_allocations - usage["allocations_count"]
        }
