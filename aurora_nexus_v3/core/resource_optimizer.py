"""
Resource Optimization System
Self-contained proactive resource optimization with prediction and automatic scaling
No external APIs - uses resource monitoring, prediction algorithms, and allocation optimization
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ResourceType(Enum):
    """Resource types"""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    WORKERS = "workers"


@dataclass
class ResourceUsage:
    """Resource usage data"""

    resource_type: ResourceType
    current_usage: float  # Percentage or absolute value
    predicted_usage: float
    capacity: float
    timestamp: datetime = field(default_factory=datetime.now)


class ResourceOptimizer:
    """
    Self-contained resource optimization system
    Proactively optimizes resources with prediction and automatic scaling
    """

    def __init__(self):
        self.resource_history: list[ResourceUsage] = []
        self.optimization_thresholds: dict[ResourceType, float] = {
            ResourceType.CPU: 80.0,
            ResourceType.MEMORY: 85.0,
            ResourceType.DISK: 90.0,
            ResourceType.NETWORK: 75.0,
            ResourceType.WORKERS: 90.0,
        }
        self.scaling_policies: dict[ResourceType, dict[str, Any]] = {}
        self._initialize_scaling_policies()

    def _initialize_scaling_policies(self):
        """Initialize scaling policies"""
        self.scaling_policies = {
            ResourceType.CPU: {
                "scale_up_threshold": 80.0,
                "scale_down_threshold": 30.0,
                "min_instances": 1,
                "max_instances": 300,
            },
            ResourceType.MEMORY: {
                "scale_up_threshold": 85.0,
                "scale_down_threshold": 40.0,
                "min_instances": 1,
                "max_instances": 300,
            },
            ResourceType.WORKERS: {
                "scale_up_threshold": 90.0,
                "scale_down_threshold": 50.0,
                "min_instances": 50,
                "max_instances": 300,
            },
        }

    def monitor_resource(self, resource_type: ResourceType, current_usage: float, capacity: float):
        """Monitor resource usage"""
        # Predict future usage
        predicted_usage = self._predict_usage(resource_type, current_usage)

        # Create usage record
        usage = ResourceUsage(
            resource_type=resource_type,
            current_usage=current_usage,
            predicted_usage=predicted_usage,
            capacity=capacity,
        )

        self.resource_history.append(usage)

        # Keep only recent history (last 10000)
        if len(self.resource_history) > 10000:
            self.resource_history = self.resource_history[-10000:]

        # Check if optimization needed
        if self._needs_optimization(usage):
            return self._optimize_resource(resource_type, usage)

        return None

    def _predict_usage(self, resource_type: ResourceType, current_usage: float) -> float:
        """Predict future resource usage"""
        # Get recent history for this resource type
        recent_usage = [u.current_usage for u in self.resource_history[-20:] if u.resource_type == resource_type]

        if not recent_usage:
            return current_usage

        # Simple trend prediction
        if len(recent_usage) >= 3:
            trend = (recent_usage[-1] - recent_usage[0]) / len(recent_usage)
            predicted = current_usage + (trend * 5)  # Predict 5 steps ahead
        else:
            predicted = current_usage

        return max(0.0, min(100.0, predicted))  # Clamp to 0-100

    def _needs_optimization(self, usage: ResourceUsage) -> bool:
        """Check if resource needs optimization"""
        threshold = self.optimization_thresholds.get(usage.resource_type, 80.0)

        # Check current usage
        if usage.current_usage > threshold:
            return True

        # Check predicted usage
        return usage.predicted_usage > threshold

    def _optimize_resource(self, resource_type: ResourceType, usage: ResourceUsage) -> dict[str, Any]:
        """Optimize resource allocation"""
        policy = self.scaling_policies.get(resource_type, {})

        optimization = {
            "resource_type": resource_type.value,
            "current_usage": usage.current_usage,
            "predicted_usage": usage.predicted_usage,
            "action": "none",
            "recommended_instances": None,
        }

        # Determine action
        if usage.current_usage > policy.get("scale_up_threshold", 80.0):
            optimization["action"] = "scale_up"
            # Calculate recommended instances
            current_instances = policy.get("current_instances", 1)
            scale_factor = usage.current_usage / policy.get("scale_up_threshold", 80.0)
            recommended = int(current_instances * scale_factor)
            recommended = min(recommended, policy.get("max_instances", 300))
            optimization["recommended_instances"] = recommended

        elif usage.current_usage < policy.get("scale_down_threshold", 30.0):
            optimization["action"] = "scale_down"
            current_instances = policy.get("current_instances", 1)
            scale_factor = usage.current_usage / policy.get("scale_down_threshold", 30.0)
            recommended = int(current_instances * scale_factor)
            recommended = max(recommended, policy.get("min_instances", 1))
            optimization["recommended_instances"] = recommended

        return optimization

    def optimize_allocation(
        self,
        tasks: list[dict[str, Any]],
        available_resources: dict[ResourceType, float],
    ) -> dict[str, Any]:
        """Optimize resource allocation for tasks"""
        allocation = {}

        # Calculate resource requirements
        total_cpu = sum(t.get("cpu_required", 1.0) for t in tasks)
        total_memory = sum(t.get("memory_required", 512.0) for t in tasks)

        # Check if resources are sufficient
        available_cpu = available_resources.get(ResourceType.CPU, 0.0)
        available_memory = available_resources.get(ResourceType.MEMORY, 0.0)

        # Optimize allocation
        if total_cpu <= available_cpu and total_memory <= available_memory:
            # All tasks can run
            allocation["feasible"] = True
            allocation["allocated_tasks"] = len(tasks)
        else:
            # Need to prioritize
            allocation["feasible"] = False
            # Sort tasks by priority
            sorted_tasks = sorted(tasks, key=lambda t: t.get("priority", 5))

            allocated = []
            used_cpu = 0.0
            used_memory = 0.0

            for task in sorted_tasks:
                task_cpu = task.get("cpu_required", 1.0)
                task_memory = task.get("memory_required", 512.0)

                if used_cpu + task_cpu <= available_cpu and used_memory + task_memory <= available_memory:
                    allocated.append(task)
                    used_cpu += task_cpu
                    used_memory += task_memory

            allocation["allocated_tasks"] = len(allocated)
            allocation["rejected_tasks"] = len(tasks) - len(allocated)

        return allocation

    def get_optimization_stats(self) -> dict[str, Any]:
        """Get optimization statistics"""
        return {
            "total_monitoring_records": len(self.resource_history),
            "resources_monitored": list(set(u.resource_type.value for u in self.resource_history)),
            "average_usage": {
                rt.value: (
                    sum(u.current_usage for u in self.resource_history if u.resource_type == rt)
                    / len([u for u in self.resource_history if u.resource_type == rt])
                    if [u for u in self.resource_history if u.resource_type == rt]
                    else 0.0
                )
                for rt in ResourceType
            },
        }
