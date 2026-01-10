"""
Aurora Task Dispatcher - Routes tasks to appropriate workers
Handles task prioritization, load balancing, and distribution
"""

import heapq
import time
import uuid
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from .worker import Task, TaskType


class DispatchStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_BUSY = "least_busy"
    PRIORITY = "priority"
    RANDOM = "random"
    AFFINITY = "affinity"


@dataclass
class TaskPriority:
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 5
    LOW = 8
    BACKGROUND = 10


class TaskDispatcher:
    """
    Dispatches tasks to workers based on strategy and priority
    Integrates with 188 Tiers, 66 AEMs, and 550 Modules
    """

    def __init__(self, worker_pool: Any = None):
        self.worker_pool = worker_pool
        self.strategy = DispatchStrategy.PRIORITY

        self.priority_queue: list[tuple] = []
        self.task_history: deque = deque(maxlen=10000)

        self.tier_routing: dict[str, str] = {}
        self.aem_routing: dict[str, TaskType] = {}
        self.module_routing: dict[str, str] = {}

        # Advanced task decomposition
        try:
            from ..core.intelligent_task_decomposer import IntelligentTaskDecomposer

            self.task_decomposer = IntelligentTaskDecomposer()
        except ImportError:
            self.task_decomposer = None

        self._initialize_routing()

    def _initialize_routing(self):
        """Initialize task routing based on tiers, AEMs, and modules"""
        self.tier_routing = {
            "code_synthesis": "code",
            "code_analysis": "analyze",
            "error_detection": "fix",
            "system_repair": "repair",
            "performance_optimization": "optimize",
            "health_monitoring": "monitor",
            "self_healing": "heal",
        }

        self.aem_routing = {
            "sequential": TaskType.CODE,
            "parallel": TaskType.ANALYZE,
            "speculative": TaskType.OPTIMIZE,
            "adversarial": TaskType.ANALYZE,
            "self_reflective": TaskType.MONITOR,
            "hybrid": TaskType.CUSTOM,
        }

    async def dispatch(self, task: Task) -> str:
        """Dispatch a task to the worker pool - Advanced with decomposition"""
        # Check if task needs decomposition
        if self.task_decomposer:
            # Check task complexity (simple heuristic)
            payload_str = str(task.payload)
            is_complex = (
                len(payload_str) > 500
                or payload_str.count("and") > 2
                or payload_str.count("then") > 1
            )

            if is_complex:
                # Decompose complex task
                decomposition = self.task_decomposer.decompose_task(task)

                # Dispatch subtasks in execution order
                subtask_ids = []
                for parallel_group in decomposition.execution_order:
                    for subtask_id in parallel_group:
                        subtask = next(
                            (st for st in decomposition.subtasks if st.subtask_id == subtask_id),
                            None,
                        )
                        if subtask and self.worker_pool:
                            # Create task from subtask
                            subtask_task = Task(
                                id=subtask.subtask_id,
                                task_type=subtask.task_type,
                                payload={"description": subtask.description, **task.payload},
                                priority=subtask.priority,
                            )
                            subtask_id = await self.worker_pool.submit_task(subtask_task)
                            subtask_ids.append(subtask_id)

                return f"decomposed:{task.id}"  # Return parent task ID

        # Standard dispatch for simple tasks
        heapq.heappush(self.priority_queue, (task.priority, time.time(), task))

        self.task_history.append(
            {
                "task_id": task.id,
                "task_type": task.task_type.value,
                "priority": task.priority,
                "dispatched_at": datetime.now().isoformat(),
            }
        )

        if self.worker_pool:
            return await self.worker_pool.submit_task(task)

        return task.id

    async def dispatch_fix(
        self, target: str, issue_type: str, priority: int = TaskPriority.MEDIUM
    ) -> str:
        """Dispatch a fix task"""
        task = Task(
            id=str(uuid.uuid4()),
            task_type=TaskType.FIX,
            payload={"target": target, "issue_type": issue_type},
            priority=priority,
        )
        return await self.dispatch(task)

    async def dispatch_code(
        self, specification: str, language: str = "python", priority: int = TaskPriority.MEDIUM
    ) -> str:
        """Dispatch a code generation task"""
        task = Task(
            id=str(uuid.uuid4()),
            task_type=TaskType.CODE,
            payload={"action": "generate", "language": language, "specification": specification},
            priority=priority,
        )
        return await self.dispatch(task)

    async def dispatch_analyze(
        self, target: str, analysis_type: str = "general", priority: int = TaskPriority.MEDIUM
    ) -> str:
        """Dispatch an analysis task"""
        task = Task(
            id=str(uuid.uuid4()),
            task_type=TaskType.ANALYZE,
            payload={"target": target, "analysis_type": analysis_type},
            priority=priority,
        )
        return await self.dispatch(task)

    async def dispatch_heal(
        self, issue: dict[str, Any], strategy: str = "auto", priority: int = TaskPriority.CRITICAL
    ) -> str:
        """Dispatch a healing task"""
        task = Task(
            id=str(uuid.uuid4()),
            task_type=TaskType.HEAL,
            payload={"issue": issue, "strategy": strategy},
            priority=priority,
        )
        return await self.dispatch(task)

    async def dispatch_batch(self, tasks: list[Task]) -> list[str]:
        """Dispatch multiple tasks at once"""
        task_ids = []
        for task in tasks:
            task_id = await self.dispatch(task)
            task_ids.append(task_id)
        return task_ids

    async def dispatch_by_tier(
        self, tier_id: str, payload: dict[str, Any], priority: int = TaskPriority.MEDIUM
    ) -> str:
        """Dispatch task based on tier routing (with optimizations)"""
        # Get tier routing suggestions if available
        if hasattr(self, "manifest_integrator") and self.manifest_integrator:
            suggestions = self.manifest_integrator.get_tier_routing_suggestions(
                payload.get("task_type", "custom"), payload
            )
            if suggestions and tier_id not in suggestions:
                # Use best matching tier
                tier_id = suggestions[0]

        task_type_str = self.tier_routing.get(tier_id, "custom")
        task_type = (
            TaskType(task_type_str)
            if task_type_str in [t.value for t in TaskType]
            else TaskType.CUSTOM
        )

        task = Task(
            id=str(uuid.uuid4()),
            task_type=task_type,
            payload={**payload, "tier_id": tier_id},
            priority=priority,
            metadata={"routed_by": "tier", "tier_id": tier_id},
        )
        return await self.dispatch(task)

    async def dispatch_by_tier_optimized(
        self, payload: dict[str, Any], priority: int = TaskPriority.MEDIUM
    ) -> str:
        """Dispatch task with automatic tier selection (optimized)"""
        # Auto-select best tier based on payload
        if hasattr(self, "manifest_integrator") and self.manifest_integrator:
            suggestions = self.manifest_integrator.get_tier_routing_suggestions(
                payload.get("task_type", "custom"), payload
            )
            if suggestions:
                tier_id = suggestions[0]
                return await self.dispatch_by_tier(tier_id, payload, priority)

        # Fallback to default routing
        return await self.dispatch_by_tier("tier-1", payload, priority)

    async def dispatch_by_aem(
        self, aem_id: str, payload: dict[str, Any], priority: int = TaskPriority.MEDIUM
    ) -> str:
        """Dispatch task based on AEM routing"""
        task_type: TaskType = self.aem_routing.get(aem_id, TaskType.CUSTOM)

        task = Task(
            id=str(uuid.uuid4()),
            task_type=task_type,
            payload={**payload, "aem_id": aem_id},
            priority=priority,
            metadata={"routed_by": "aem", "aem_id": aem_id},
        )
        return await self.dispatch(task)

    def get_pending_count(self) -> int:
        """Get count of pending tasks"""
        return len(self.priority_queue)

    def get_next_task(self) -> Task | None:
        """Get next task from priority queue"""
        if self.priority_queue:
            _, _, task = heapq.heappop(self.priority_queue)
            return task
        return None

    def get_status(self) -> dict[str, Any]:
        """Get dispatcher status"""
        return {
            "strategy": self.strategy.value,
            "pending_tasks": len(self.priority_queue),
            "history_size": len(self.task_history),
            "tier_routes": len(self.tier_routing),
            "aem_routes": len(self.aem_routing),
        }
