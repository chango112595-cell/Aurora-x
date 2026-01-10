"""
Advanced AEM Management System
Self-contained intelligent AEM management with capability matching and optimization
No external APIs - uses pattern matching and capability analysis
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class AEMStatus(Enum):
    """AEM status"""

    AVAILABLE = "available"
    IN_USE = "in_use"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


@dataclass
class AEMAssignment:
    """AEM assignment"""

    assignment_id: str
    aem_id: str
    task_id: str
    assigned_at: datetime
    capabilities_used: list[str]


class AdvancedAEMManager:
    """
    Self-contained advanced AEM management system
    Intelligently manages AEM resources and assignments
    """

    def __init__(self):
        self.aem_statuses: dict[str, AEMStatus] = {}
        self.aem_capabilities: dict[str, list[str]] = {}  # aem_id -> [capabilities]
        self.aem_assignments: list[AEMAssignment] = []
        self.aem_performance: dict[str, dict[str, Any]] = {}  # aem_id -> performance_metrics

    def assign_aem(
        self,
        task_id: str,
        required_capabilities: list[str],
    ) -> AEMAssignment | None:
        """Assign an AEM to a task"""
        # Find suitable AEM
        suitable_aem = self._find_suitable_aem(required_capabilities)

        if not suitable_aem:
            return None

        # Create assignment
        assignment = AEMAssignment(
            assignment_id=str(uuid.uuid4()),
            aem_id=suitable_aem,
            task_id=task_id,
            assigned_at=datetime.now(),
            capabilities_used=required_capabilities,
        )

        self.aem_assignments.append(assignment)
        self.aem_statuses[suitable_aem] = AEMStatus.IN_USE

        return assignment

    def _find_suitable_aem(self, required_capabilities: list[str]) -> str | None:
        """Find suitable AEM"""
        # Find AEMs with required capabilities
        suitable_aems = []

        for aem_id, capabilities in self.aem_capabilities.items():
            if all(cap in capabilities for cap in required_capabilities):
                status = self.aem_statuses.get(aem_id, AEMStatus.AVAILABLE)
                if status == AEMStatus.AVAILABLE:
                    # Check performance
                    performance = self.aem_performance.get(aem_id, {})
                    success_rate = performance.get("success_rate", 1.0)
                    suitable_aems.append((aem_id, success_rate))

        if not suitable_aems:
            return None

        # Select AEM with best performance
        suitable_aems.sort(key=lambda x: x[1], reverse=True)
        return suitable_aems[0][0]

    def release_aem(self, assignment_id: str):
        """Release AEM assignment"""
        assignment = next(
            (a for a in self.aem_assignments if a.assignment_id == assignment_id), None
        )

        if assignment:
            self.aem_statuses[assignment.aem_id] = AEMStatus.AVAILABLE
            self.aem_assignments = [
                a for a in self.aem_assignments if a.assignment_id != assignment_id
            ]

    def update_aem_performance(self, aem_id: str, success: bool, execution_time_ms: float):
        """Update AEM performance metrics"""
        if aem_id not in self.aem_performance:
            self.aem_performance[aem_id] = {
                "total_tasks": 0,
                "successful_tasks": 0,
                "total_time_ms": 0.0,
                "success_rate": 1.0,
                "avg_time_ms": 0.0,
            }

        metrics = self.aem_performance[aem_id]
        metrics["total_tasks"] += 1
        if success:
            metrics["successful_tasks"] += 1
        metrics["total_time_ms"] += execution_time_ms

        metrics["success_rate"] = metrics["successful_tasks"] / metrics["total_tasks"]
        metrics["avg_time_ms"] = metrics["total_time_ms"] / metrics["total_tasks"]

    def get_aem_stats(self) -> dict[str, Any]:
        """Get AEM statistics"""
        return {
            "total_aems": len(self.aem_statuses),
            "aems_by_status": {
                status.value: len([a for a, s in self.aem_statuses.items() if s == status])
                for status in AEMStatus
            },
            "total_assignments": len(self.aem_assignments),
            "average_success_rate": (
                sum(p.get("success_rate", 0.0) for p in self.aem_performance.values())
                / len(self.aem_performance)
                if self.aem_performance
                else 0.0
            ),
        }
