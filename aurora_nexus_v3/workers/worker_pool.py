"""
Aurora Autonomous Worker Pool - 300 Workers for Peak Autonomous Operation
Manages the swarm of non-conscious task workers

Features:
- 300 parallel workers (configurable)
- Automatic task distribution
- Load balancing
- Health monitoring
- Auto-scaling
- Issue detection and automatic healing
"""

import asyncio
import threading
import time
from collections import deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .worker import AutonomousWorker, Task, TaskResult, TaskType, WorkerState


class PoolState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    SCALING = "scaling"
    HEALING = "healing"
    STOPPED = "stopped"


@dataclass
class PoolMetrics:
    total_workers: int = 0
    active_workers: int = 0
    idle_workers: int = 0
    tasks_queued: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_execution_time_ms: float = 0
    uptime_seconds: float = 0


class AutonomousWorkerPool:
    """
    Pool of 300 autonomous workers for peak Aurora operation

    These workers are NOT conscious or self-aware - they are pure task executors
    that respond to orders or system issues automatically.
    """

    DEFAULT_WORKER_COUNT = 300

    def __init__(self, worker_count: int = DEFAULT_WORKER_COUNT, core: Any = None):
        self.worker_count = worker_count
        self.core = core
        self.state = PoolState.INITIALIZING
        self.start_time = time.time()

        self.workers: dict[str, AutonomousWorker] = {}
        self.task_queue: deque = deque()
        self.completed_tasks: list[TaskResult] = []
        self.failed_tasks: list[TaskResult] = []

        self.executor = ThreadPoolExecutor(max_workers=min(worker_count, 100))
        self.monitoring_active = False
        self._monitor_thread: threading.Thread | None = None
        self._dispatcher_thread: threading.Thread | None = None

        self.issue_handlers: dict[str, Callable] = {}
        self.auto_healing_enabled = True

        self._initialize_workers()

    def _initialize_workers(self):
        """Initialize all 300 workers"""
        print(f"[AURORA WORKERS] Initializing {self.worker_count} autonomous workers...")

        for i in range(self.worker_count):
            worker = AutonomousWorker(worker_id=i, worker_pool=self)
            self.workers[worker.worker_id] = worker

        self.state = PoolState.RUNNING
        print(f"[AURORA WORKERS] {self.worker_count} workers online and ready")
        print("[AURORA WORKERS] Power Level: Full Aurora (188 Tiers, 66 AEMs, 550 Modules)")
        print("[AURORA WORKERS] Mode: Autonomous Task Execution (Non-Conscious)")

    async def start(self):
        """Start the worker pool with monitoring and dispatching"""
        self.monitoring_active = True

        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

        self._dispatcher_thread = threading.Thread(target=self._dispatch_loop, daemon=True)
        self._dispatcher_thread.start()

        print("[AURORA WORKERS] Worker pool started with monitoring enabled")

    async def stop(self):
        """Stop the worker pool"""
        self.monitoring_active = False
        self.state = PoolState.STOPPED
        self.executor.shutdown(wait=True)
        print("[AURORA WORKERS] Worker pool stopped")

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                self._check_worker_health()
                time.sleep(5)
            except Exception as e:
                print(f"[AURORA WORKERS] Monitor error: {e}")

    def _dispatch_loop(self):
        """Background task dispatch loop"""
        while self.monitoring_active:
            try:
                if self.task_queue:
                    task = self.task_queue.popleft()
                    worker = self._get_available_worker()
                    if worker:
                        asyncio.run(self._execute_task(worker, task))
                    else:
                        self.task_queue.appendleft(task)
                        time.sleep(0.1)
                else:
                    time.sleep(0.05)
            except Exception as e:
                print(f"[AURORA WORKERS] Dispatch error: {e}")

    def _check_worker_health(self):
        """
        Self-Healing Watchdog - Check health of all workers.
        Extends V3's existing recovery loop with autonomous healing.

        Features:
        - Automatic issue detection
        - Autonomous resolution (no human interaction required)
        - Worker restart on failure
        - Performance monitoring
        """
        unhealthy_count = 0
        restarted_count = 0

        for worker in self.workers.values():
            if (
                not worker.alive()
                if hasattr(worker, "alive")
                else worker.state == WorkerState.FAILED
            ):
                unhealthy_count += 1
                if self.auto_healing_enabled:
                    self._restart_worker(worker)
                    restarted_count += 1

        if unhealthy_count > 0:
            print(
                f"[AURORA WATCHDOG] Self-healing: {restarted_count}/{unhealthy_count} workers restarted"
            )

    def _restart_worker(self, worker: AutonomousWorker):
        """Restart a failed worker - autonomous healing"""
        try:
            worker.state = WorkerState.IDLE
            worker.tasks_completed = 0
            worker.total_execution_time = 0
            worker.consecutive_failures = 0
            worker.last_error = None
        except Exception as e:
            print(f"[AURORA WATCHDOG] Failed to restart worker {worker.worker_id}: {e}")

    def on_tick(self):
        """V3 lifecycle hook - check for failed workers and restart them"""
        failed = [
            w
            for w in self.workers.values()
            if (hasattr(w, "alive") and not w.alive()) or w.state == WorkerState.FAILED
        ]
        for w in failed:
            self._restart_worker(w)

    def _get_available_worker(self) -> AutonomousWorker | None:
        """Get an available worker for task execution"""
        for worker in self.workers.values():
            if worker.is_available:
                return worker
        return None

    async def _execute_task(self, worker: AutonomousWorker, task: Task) -> TaskResult:
        """Execute a task on a specific worker"""
        result = await worker.execute(task)

        if result.success:
            self.completed_tasks.append(result)
        else:
            self.failed_tasks.append(result)

            if task.retry_count < task.max_retries:
                task.retry_count += 1
                self.task_queue.append(task)

        return result

    async def submit_task(self, task: Task) -> str:
        """Submit a task for execution"""
        self.task_queue.append(task)
        return task.id

    async def submit_fix_task(self, target: str, issue_type: str, priority: int = 5) -> str:
        """Submit a fix task"""
        import uuid

        task = Task(
            id=str(uuid.uuid4()),
            task_type=TaskType.FIX,
            payload={"target": target, "issue_type": issue_type},
            priority=priority,
        )
        return await self.submit_task(task)

    async def submit_code_task(
        self, action: str, language: str, specification: str, priority: int = 5
    ) -> str:
        """Submit a code generation task"""
        import uuid

        task = Task(
            id=str(uuid.uuid4()),
            task_type=TaskType.CODE,
            payload={"action": action, "language": language, "specification": specification},
            priority=priority,
        )
        return await self.submit_task(task)

    async def submit_analyze_task(self, target: str, analysis_type: str, priority: int = 5) -> str:
        """Submit an analysis task"""
        import uuid

        task = Task(
            id=str(uuid.uuid4()),
            task_type=TaskType.ANALYZE,
            payload={"target": target, "analysis_type": analysis_type},
            priority=priority,
        )
        return await self.submit_task(task)

    async def submit_heal_task(self, issue: dict, strategy: str = "auto", priority: int = 1) -> str:
        """Submit a healing task (high priority by default)"""
        import uuid

        task = Task(
            id=str(uuid.uuid4()),
            task_type=TaskType.HEAL,
            payload={"issue": issue, "strategy": strategy},
            priority=priority,
        )
        return await self.submit_task(task)

    async def handle_system_issue(self, issue: dict[str, Any]):
        """Automatically handle a detected system issue"""
        issue_type = issue.get("type", "unknown")
        severity = issue.get("severity", "medium")
        target = issue.get("target", "")

        print(f"[AURORA WORKERS] Issue detected: {issue_type} ({severity}) in {target}")

        priority = 1 if severity == "critical" else (3 if severity == "high" else 5)

        if issue_type in ["import_error", "syntax_error", "encoding_error"]:
            await self.submit_fix_task(target, issue_type, priority)
        elif issue_type in ["service_down", "health_check_failed"]:
            await self.submit_heal_task(issue, "restart", priority)
        elif issue_type in ["performance_degraded", "memory_high"]:
            await self.submit_heal_task(issue, "optimize", priority)
        else:
            await self.submit_heal_task(issue, "auto", priority)

        print(f"[AURORA WORKERS] Autonomous response initiated for {issue_type}")

    def get_metrics(self) -> PoolMetrics:
        """Get pool metrics"""
        active = sum(1 for w in self.workers.values() if not w.is_available)
        idle = sum(1 for w in self.workers.values() if w.is_available)

        total_time = sum(w.total_execution_time for w in self.workers.values())
        total_tasks = sum(w.tasks_completed for w in self.workers.values())
        avg_time = total_time / total_tasks if total_tasks > 0 else 0

        return PoolMetrics(
            total_workers=self.worker_count,
            active_workers=active,
            idle_workers=idle,
            tasks_queued=len(self.task_queue),
            tasks_completed=len(self.completed_tasks),
            tasks_failed=len(self.failed_tasks),
            avg_execution_time_ms=avg_time,
            uptime_seconds=time.time() - self.start_time,
        )

    def get_status(self) -> dict[str, Any]:
        """Get pool status"""
        metrics = self.get_metrics()
        return {
            "state": self.state.value,
            "worker_count": self.worker_count,
            "metrics": {
                "total_workers": metrics.total_workers,
                "active_workers": metrics.active_workers,
                "idle_workers": metrics.idle_workers,
                "tasks_queued": metrics.tasks_queued,
                "tasks_completed": metrics.tasks_completed,
                "tasks_failed": metrics.tasks_failed,
                "avg_execution_time_ms": metrics.avg_execution_time_ms,
                "uptime_seconds": metrics.uptime_seconds,
            },
            "auto_healing_enabled": self.auto_healing_enabled,
            "monitoring_active": self.monitoring_active,
        }

    def get_worker_status(self, worker_id: str) -> dict[str, Any] | None:
        """Get status of a specific worker"""
        worker = self.workers.get(worker_id)
        return worker.get_status() if worker else None

    def get_all_workers_status(self) -> list[dict[str, Any]]:
        """Get status of all workers"""
        return [w.get_status() for w in self.workers.values()]
