"""
Advanced Task Orchestration System
Self-contained intelligent task orchestration with dynamic scheduling and optimization
No external APIs - uses scheduling algorithms, resource optimization, and load balancing
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from ..workers.worker import Task, TaskType
from .autonomous_decision_engine import AutonomousDecisionEngine, DecisionType
from .intelligent_task_decomposer import IntelligentTaskDecomposer


class SchedulingStrategy(Enum):
    """Task scheduling strategies"""

    FIFO = "fifo"  # First in, first out
    PRIORITY = "priority"  # Priority-based
    DEADLINE = "deadline"  # Deadline-based
    RESOURCE_AWARE = "resource_aware"  # Resource optimization
    LOAD_BALANCED = "load_balanced"  # Load balancing
    ADAPTIVE = "adaptive"  # Adaptive based on conditions


@dataclass
class OrchestrationPlan:
    """An orchestration plan"""

    plan_id: str
    tasks: list[Task]
    schedule: list[dict[str, Any]]  # Task assignments with timing
    resource_allocation: dict[str, Any]
    estimated_completion: datetime
    optimization_score: float
    strategy: SchedulingStrategy


class AdvancedTaskOrchestrator:
    """
    Self-contained advanced task orchestration system
    Intelligently schedules and optimizes task execution
    """

    def __init__(self):
        self.task_decomposer = IntelligentTaskDecomposer()
        self.decision_engine = AutonomousDecisionEngine()
        self.orchestration_history: list[OrchestrationPlan] = []
        self.task_dependencies: dict[str, list[str]] = {}  # task_id -> [dependent_task_ids]
        self.resource_usage: dict[str, float] = {}  # resource_type -> usage
        self.worker_loads: dict[str, int] = {}  # worker_id -> load
        self.scheduling_strategies: dict[str, SchedulingStrategy] = {}

    def orchestrate_tasks(
        self,
        tasks: list[Task],
        strategy: SchedulingStrategy = SchedulingStrategy.ADAPTIVE,
    ) -> OrchestrationPlan:
        """
        Orchestrate multiple tasks intelligently
        """
        plan_id = str(uuid.uuid4())

        # Step 1: Decompose complex tasks
        decomposed_tasks = []
        for task in tasks:
            decomposition = self.task_decomposer.decompose_task(task)
            if len(decomposition.subtasks) > 1:
                # Add subtasks
                for subtask in decomposition.subtasks:
                    subtask_task = Task(
                        id=subtask.subtask_id,
                        task_type=subtask.task_type,
                        payload={"description": subtask.description, **task.payload},
                        priority=subtask.priority,
                    )
                    decomposed_tasks.append(subtask_task)
                    # Track dependencies
                    if subtask.dependencies:
                        self.task_dependencies[subtask.subtask_id] = subtask.dependencies
            else:
                decomposed_tasks.append(task)

        all_tasks = tasks + decomposed_tasks

        # Step 2: Determine optimal strategy
        if strategy == SchedulingStrategy.ADAPTIVE:
            strategy = self._determine_optimal_strategy(all_tasks)

        # Step 3: Schedule tasks
        schedule = self._schedule_tasks(all_tasks, strategy)

        # Step 4: Allocate resources
        resource_allocation = self._allocate_resources(all_tasks, schedule)

        # Step 5: Estimate completion
        estimated_completion = self._estimate_completion(schedule)

        # Step 6: Calculate optimization score
        optimization_score = self._calculate_optimization_score(
            schedule, resource_allocation, all_tasks
        )

        # Create orchestration plan
        plan = OrchestrationPlan(
            plan_id=plan_id,
            tasks=all_tasks,
            schedule=schedule,
            resource_allocation=resource_allocation,
            estimated_completion=estimated_completion,
            optimization_score=optimization_score,
            strategy=strategy,
        )

        self.orchestration_history.append(plan)

        # Keep only recent plans (last 1000)
        if len(self.orchestration_history) > 1000:
            self.orchestration_history = self.orchestration_history[-1000:]

        return plan

    def _determine_optimal_strategy(self, tasks: list[Task]) -> SchedulingStrategy:
        """Determine optimal scheduling strategy"""
        # Analyze task characteristics
        has_deadlines = any(task.metadata.get("deadline") for task in tasks)
        has_priorities = any(task.priority < 5 for task in tasks)
        resource_intensive = any("resource" in str(task.payload).lower() for task in tasks)

        # Use decision engine to choose strategy
        context = {
            "has_deadlines": has_deadlines,
            "has_priorities": has_priorities,
            "resource_intensive": resource_intensive,
            "task_count": len(tasks),
        }

        decision = self.decision_engine.make_decision(
            DecisionType.TACTICAL,
            context,
            options=[
                "Use priority-based scheduling",
                "Use deadline-based scheduling",
                "Use resource-aware scheduling",
                "Use load-balanced scheduling",
            ],
        )

        # Map decision to strategy
        if decision.selected_option:
            option_desc = decision.selected_option.description.lower()
            if "priority" in option_desc:
                return SchedulingStrategy.PRIORITY
            elif "deadline" in option_desc:
                return SchedulingStrategy.DEADLINE
            elif "resource" in option_desc:
                return SchedulingStrategy.RESOURCE_AWARE
            elif "load" in option_desc:
                return SchedulingStrategy.LOAD_BALANCED

        return SchedulingStrategy.PRIORITY  # Default

    def _schedule_tasks(
        self,
        tasks: list[Task],
        strategy: SchedulingStrategy,
    ) -> list[dict[str, Any]]:
        """Schedule tasks based on strategy"""
        schedule = []

        if strategy == SchedulingStrategy.PRIORITY:
            # Sort by priority
            sorted_tasks = sorted(tasks, key=lambda t: t.priority)
        elif strategy == SchedulingStrategy.DEADLINE:
            # Sort by deadline
            sorted_tasks = sorted(
                tasks,
                key=lambda t: t.metadata.get("deadline", datetime.max),
            )
        elif strategy == SchedulingStrategy.FIFO:
            # First in, first out
            sorted_tasks = tasks
        else:
            # Default to priority
            sorted_tasks = sorted(tasks, key=lambda t: t.priority)

        # Create schedule entries
        current_time = datetime.now()
        for _i, task in enumerate(sorted_tasks):
            # Check dependencies
            dependencies = self.task_dependencies.get(task.id, [])

            schedule_entry = {
                "task_id": task.id,
                "task_type": task.task_type.value,
                "priority": task.priority,
                "scheduled_time": current_time,
                "dependencies": dependencies,
                "estimated_duration_ms": task.timeout_ms,
                "worker_assignment": None,  # Will be assigned by dispatcher
            }

            schedule.append(schedule_entry)

            # Advance time (simplified)
            current_time = datetime.fromtimestamp(current_time.timestamp() + task.timeout_ms / 1000)

        return schedule

    def _allocate_resources(
        self,
        tasks: list[Task],
        schedule: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Allocate resources for tasks"""
        allocation = {
            "cpu_cores": 0,
            "memory_mb": 0,
            "workers": 0,
            "estimated_total_time_ms": 0,
        }

        # Calculate resource needs
        for task in tasks:
            # Estimate resources based on task type
            if task.task_type == TaskType.CODE:
                allocation["cpu_cores"] += 1
                allocation["memory_mb"] += 512
            elif task.task_type == TaskType.ANALYZE:
                allocation["cpu_cores"] += 2
                allocation["memory_mb"] += 1024
            elif task.task_type == TaskType.OPTIMIZE:
                allocation["cpu_cores"] += 1
                allocation["memory_mb"] += 256

        # Estimate workers needed
        allocation["workers"] = min(len(tasks), 300)  # Max 300 workers

        # Estimate total time
        allocation["estimated_total_time_ms"] = sum(
            entry["estimated_duration_ms"] for entry in schedule
        )

        return allocation

    def _estimate_completion(self, schedule: list[dict[str, Any]]) -> datetime:
        """Estimate completion time"""
        if not schedule:
            return datetime.now()

        # Find latest scheduled time + duration
        latest_entry = max(schedule, key=lambda e: e["scheduled_time"].timestamp())
        completion_time = latest_entry["scheduled_time"].timestamp() + (
            latest_entry["estimated_duration_ms"] / 1000
        )

        return datetime.fromtimestamp(completion_time)

    def _calculate_optimization_score(
        self,
        schedule: list[dict[str, Any]],
        resource_allocation: dict[str, Any],
        tasks: list[Task],
    ) -> float:
        """Calculate optimization score"""
        score = 1.0

        # Factor 1: Resource utilization
        resource_efficiency = 1.0 - (resource_allocation.get("cpu_cores", 0) / 100.0)  # Normalize
        score *= resource_efficiency

        # Factor 2: Task parallelism
        parallel_tasks = len([e for e in schedule if not e.get("dependencies")])
        parallelism_score = min(parallel_tasks / len(tasks), 1.0) if tasks else 0.0
        score *= 0.5 + parallelism_score * 0.5

        # Factor 3: Priority adherence
        priority_violations = sum(
            1
            for i, entry in enumerate(schedule)
            if i > 0 and entry["priority"] < schedule[i - 1]["priority"]
        )
        priority_score = 1.0 - (priority_violations / len(schedule)) if schedule else 1.0
        score *= priority_score

        return max(0.0, min(1.0, score))

    def optimize_schedule(self, plan: OrchestrationPlan) -> OrchestrationPlan:
        """Optimize an existing schedule"""
        # Re-orchestrate with optimization
        optimized_plan = self.orchestrate_tasks(
            plan.tasks,
            strategy=SchedulingStrategy.RESOURCE_AWARE,
        )

        return optimized_plan

    def get_orchestration_stats(self) -> dict[str, Any]:
        """Get orchestration statistics"""
        return {
            "total_plans": len(self.orchestration_history),
            "average_optimization_score": (
                sum(p.optimization_score for p in self.orchestration_history)
                / len(self.orchestration_history)
                if self.orchestration_history
                else 0.0
            ),
            "strategies_used": list(set(p.strategy.value for p in self.orchestration_history)),
        }
