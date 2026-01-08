"""
Aurora Pack 09: Compute Layer

Production-ready distributed computing and task execution layer.
Manages compute resources, workload distribution, and parallel processing.

Author: Aurora AI System
Version: 2.0.0
"""

import hashlib
import json
import os
import queue
import threading
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

PACK_ID = "pack09"
PACK_NAME = "Compute Layer"
PACK_VERSION = "2.0.0"


class TaskStatus(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class ComputeTask:
    task_id: str
    name: str
    payload: dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: str | None = None
    completed_at: str | None = None
    result: Any | None = None
    error: str | None = None
    worker_id: str | None = None
    retries: int = 0
    max_retries: int = 3


@dataclass
class ComputeWorker:
    worker_id: str
    status: str = "idle"
    current_task: str | None = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ResourceMetrics:
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    active_workers: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0


class TaskQueue:
    def __init__(self):
        self._queues: dict[TaskPriority, queue.Queue] = {
            priority: queue.Queue() for priority in TaskPriority
        }
        self._lock = threading.Lock()
        self._task_index: dict[str, ComputeTask] = {}

    def enqueue(self, task: ComputeTask):
        with self._lock:
            task.status = TaskStatus.QUEUED
            self._queues[task.priority].put(task)
            self._task_index[task.task_id] = task

    def dequeue(self) -> ComputeTask | None:
        for priority in [
            TaskPriority.CRITICAL,
            TaskPriority.HIGH,
            TaskPriority.NORMAL,
            TaskPriority.LOW,
        ]:
            try:
                task = self._queues[priority].get_nowait()
                return task
            except queue.Empty:
                continue
        return None

    def get_task(self, task_id: str) -> ComputeTask | None:
        return self._task_index.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        task = self._task_index.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.QUEUED]:
            task.status = TaskStatus.CANCELLED
            return True
        return False

    def pending_count(self) -> int:
        return sum(q.qsize() for q in self._queues.values())

    def get_all_tasks(self) -> list[ComputeTask]:
        return list(self._task_index.values())


class WorkerPool:
    def __init__(self, num_workers: int = 10):
        self.num_workers = num_workers
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.workers: dict[str, ComputeWorker] = {}
        self.futures: dict[str, Future] = {}
        self._lock = threading.Lock()
        self._running = True
        self._init_workers()

    def _init_workers(self):
        for i in range(self.num_workers):
            worker_id = f"worker-{i:03d}"
            self.workers[worker_id] = ComputeWorker(worker_id=worker_id)

    def get_available_worker(self) -> ComputeWorker | None:
        with self._lock:
            for worker in self.workers.values():
                if worker.status == "idle":
                    return worker
        return None

    def assign_task(self, worker: ComputeWorker, task: ComputeTask, task_func: Callable) -> Future:
        with self._lock:
            worker.status = "busy"
            worker.current_task = task.task_id
            worker.last_activity = datetime.now().isoformat()
            task.worker_id = worker.worker_id
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now().isoformat()

        future = self.executor.submit(self._execute_task, worker, task, task_func)
        self.futures[task.task_id] = future
        return future

    def _execute_task(self, worker: ComputeWorker, task: ComputeTask, task_func: Callable) -> Any:
        try:
            result = task_func(task.payload)
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now().isoformat()
            worker.tasks_completed += 1
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now().isoformat()
            worker.tasks_failed += 1
        finally:
            with self._lock:
                worker.status = "idle"
                worker.current_task = None
                worker.last_activity = datetime.now().isoformat()

        return task.result

    def get_worker_stats(self) -> dict[str, Any]:
        with self._lock:
            idle = sum(1 for w in self.workers.values() if w.status == "idle")
            busy = sum(1 for w in self.workers.values() if w.status == "busy")
            total_completed = sum(w.tasks_completed for w in self.workers.values())
            total_failed = sum(w.tasks_failed for w in self.workers.values())

        return {
            "total_workers": self.num_workers,
            "idle": idle,
            "busy": busy,
            "total_completed": total_completed,
            "total_failed": total_failed,
        }

    def shutdown(self, wait: bool = True):
        self._running = False
        self.executor.shutdown(wait=wait)


class ResourceMonitor:
    def __init__(self):
        self.metrics = ResourceMetrics()
        self._lock = threading.Lock()

    def update_metrics(self, worker_pool: WorkerPool, task_queue: TaskQueue):
        with self._lock:
            try:
                import psutil

                self.metrics.cpu_percent = psutil.cpu_percent()
                self.metrics.memory_percent = psutil.virtual_memory().percent
                self.metrics.disk_percent = psutil.disk_usage("/").percent
            except ImportError:
                self.metrics.cpu_percent = 0.0
                self.metrics.memory_percent = 0.0
                self.metrics.disk_percent = 0.0

            stats = worker_pool.get_worker_stats()
            self.metrics.active_workers = stats["busy"]
            self.metrics.pending_tasks = task_queue.pending_count()
            self.metrics.running_tasks = stats["busy"]

    def get_metrics(self) -> ResourceMetrics:
        with self._lock:
            return ResourceMetrics(
                cpu_percent=self.metrics.cpu_percent,
                memory_percent=self.metrics.memory_percent,
                disk_percent=self.metrics.disk_percent,
                active_workers=self.metrics.active_workers,
                pending_tasks=self.metrics.pending_tasks,
                running_tasks=self.metrics.running_tasks,
            )

    def should_scale_up(self) -> bool:
        return (
            self.metrics.pending_tasks > self.metrics.active_workers * 2
            and self.metrics.cpu_percent < 80
        )

    def should_scale_down(self) -> bool:
        return (
            self.metrics.pending_tasks == 0
            and self.metrics.active_workers > 1
            and self.metrics.cpu_percent < 20
        )


class TaskExecutors:
    @staticmethod
    def echo_executor(payload: dict[str, Any]) -> Any:
        return {"echo": payload}

    @staticmethod
    def compute_executor(payload: dict[str, Any]) -> Any:
        operation = payload.get("operation", "add")
        values = payload.get("values", [])

        if operation == "add":
            return {"result": sum(values)}
        elif operation == "multiply":
            result = 1
            for v in values:
                result *= v
            return {"result": result}
        elif operation == "hash":
            data = payload.get("data", "")
            return {"result": hashlib.sha256(data.encode()).hexdigest()}
        else:
            return {"error": f"Unknown operation: {operation}"}

    @staticmethod
    def delay_executor(payload: dict[str, Any]) -> Any:
        delay = payload.get("delay", 1)
        time.sleep(min(delay, 10))
        return {"delayed": delay}


class ComputeLayer:
    def __init__(self, num_workers: int = 10, state_dir: str = "/tmp/aurora_compute"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.task_queue = TaskQueue()
        self.worker_pool = WorkerPool(num_workers)
        self.monitor = ResourceMonitor()

        self.executors: dict[str, Callable] = {
            "echo": TaskExecutors.echo_executor,
            "compute": TaskExecutors.compute_executor,
            "delay": TaskExecutors.delay_executor,
        }

        self._scheduler_thread: threading.Thread | None = None
        self._running = False

    def register_executor(self, name: str, executor: Callable):
        self.executors[name] = executor

    def submit_task(
        self,
        name: str,
        payload: dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        executor_name: str = "echo",
    ) -> str:
        task_id = hashlib.md5(
            f"{name}{datetime.now().isoformat()}{id(payload)}".encode()
        ).hexdigest()[:16]

        task = ComputeTask(
            task_id=task_id,
            name=name,
            payload={**payload, "_executor": executor_name},
            priority=priority,
        )

        self.task_queue.enqueue(task)
        self._process_queue()

        return task_id

    def _process_queue(self):
        while True:
            task = self.task_queue.dequeue()
            if not task:
                break

            worker = self.worker_pool.get_available_worker()
            if not worker:
                self.task_queue.enqueue(task)
                break

            executor_name = task.payload.get("_executor", "echo")
            executor = self.executors.get(executor_name, TaskExecutors.echo_executor)

            self.worker_pool.assign_task(worker, task, executor)

    def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        task = self.task_queue.get_task(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status.value,
            "priority": task.priority.name,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "result": task.result,
            "error": task.error,
            "worker_id": task.worker_id,
        }

    def cancel_task(self, task_id: str) -> bool:
        return self.task_queue.cancel_task(task_id)

    def get_queue_status(self) -> dict[str, Any]:
        self.monitor.update_metrics(self.worker_pool, self.task_queue)
        metrics = self.monitor.get_metrics()
        worker_stats = self.worker_pool.get_worker_stats()

        return {
            "pending_tasks": metrics.pending_tasks,
            "running_tasks": metrics.running_tasks,
            "workers": worker_stats,
            "resources": {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "disk_percent": metrics.disk_percent,
            },
        }

    def get_all_tasks(self) -> list[dict[str, Any]]:
        tasks = self.task_queue.get_all_tasks()
        return [
            {
                "task_id": t.task_id,
                "name": t.name,
                "status": t.status.value,
                "priority": t.priority.name,
            }
            for t in tasks
        ]

    def shutdown(self):
        self._running = False
        self.worker_pool.shutdown()


def get_pack_info():
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "version": PACK_VERSION,
        "status": "production",
        "components": ["TaskQueue", "WorkerPool", "ResourceMonitor", "ComputeLayer"],
        "features": [
            "Priority-based task queue (4 levels)",
            "Thread pool with configurable workers",
            "Resource monitoring and auto-scaling hints",
            "Pluggable task executors",
            "Task status tracking and cancellation",
        ],
    }
