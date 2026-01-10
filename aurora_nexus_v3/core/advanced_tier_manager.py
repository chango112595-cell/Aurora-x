"""
Advanced Tier Management System
Self-contained intelligent tier management with dynamic allocation and optimization
No external APIs - uses resource allocation algorithms and load balancing
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class TierStatus(Enum):
    """Tier status"""

    ACTIVE = "active"
    IDLE = "idle"
    OVERLOADED = "overloaded"
    MAINTENANCE = "maintenance"


@dataclass
class TierAllocation:
    """Tier allocation"""

    allocation_id: str
    tier_id: str
    task_id: str
    allocated_at: datetime
    estimated_completion: datetime
    resources_allocated: dict[str, Any]


class AdvancedTierManager:
    """
    Self-contained advanced tier management system
    Intelligently manages tier resources and allocations
    """

    def __init__(self):
        self.tier_statuses: dict[str, TierStatus] = {}
        self.tier_loads: dict[str, int] = {}  # tier_id -> load
        self.tier_capabilities: dict[str, list[str]] = {}  # tier_id -> [capabilities]
        self.allocations: list[TierAllocation] = []
        self.tier_history: dict[str, list[dict[str, Any]]] = {}

    def allocate_tier(
        self,
        task_id: str,
        required_capabilities: list[str],
        priority: int = 5,
    ) -> TierAllocation | None:
        """Allocate a tier for a task"""
        # Find suitable tier
        suitable_tier = self._find_suitable_tier(required_capabilities, priority)

        if not suitable_tier:
            return None

        # Create allocation
        allocation = TierAllocation(
            allocation_id=str(uuid.uuid4()),
            tier_id=suitable_tier,
            task_id=task_id,
            allocated_at=datetime.now(),
            estimated_completion=datetime.now(),  # Simplified
            resources_allocated={"capabilities": required_capabilities},
        )

        self.allocations.append(allocation)

        # Update tier load
        self.tier_loads[suitable_tier] = self.tier_loads.get(suitable_tier, 0) + 1

        # Update tier status
        if self.tier_loads[suitable_tier] > 10:
            self.tier_statuses[suitable_tier] = TierStatus.OVERLOADED
        else:
            self.tier_statuses[suitable_tier] = TierStatus.ACTIVE

        return allocation

    def _find_suitable_tier(
        self,
        required_capabilities: list[str],
        priority: int,
    ) -> str | None:
        """Find suitable tier for task"""
        # Find tiers with required capabilities
        suitable_tiers = []

        for tier_id, capabilities in self.tier_capabilities.items():
            if all(cap in capabilities for cap in required_capabilities):
                # Check if tier is available
                status = self.tier_statuses.get(tier_id, TierStatus.IDLE)
                if status != TierStatus.MAINTENANCE:
                    load = self.tier_loads.get(tier_id, 0)
                    suitable_tiers.append((tier_id, load))

        if not suitable_tiers:
            return None

        # Select tier with lowest load
        suitable_tiers.sort(key=lambda x: x[1])
        return suitable_tiers[0][0]

    def release_tier(self, allocation_id: str):
        """Release tier allocation"""
        allocation = next((a for a in self.allocations if a.allocation_id == allocation_id), None)

        if allocation:
            # Update tier load
            tier_id = allocation.tier_id
            if tier_id in self.tier_loads:
                self.tier_loads[tier_id] = max(0, self.tier_loads[tier_id] - 1)

            # Update tier status
            if self.tier_loads.get(tier_id, 0) == 0:
                self.tier_statuses[tier_id] = TierStatus.IDLE

            # Remove allocation
            self.allocations = [a for a in self.allocations if a.allocation_id != allocation_id]

    def optimize_tier_allocation(self):
        """Optimize tier allocations"""
        # Rebalance loads
        total_load = sum(self.tier_loads.values())
        tier_count = len(self.tier_loads)

        if tier_count == 0:
            return

        target_load = total_load / tier_count

        # Identify overloaded and underloaded tiers
        # (Simplified - real implementation would redistribute tasks)
        # This is a placeholder for optimization logic

    def get_tier_stats(self) -> dict[str, Any]:
        """Get tier statistics"""
        return {
            "total_tiers": len(self.tier_statuses),
            "tiers_by_status": {
                status.value: len([t for t, s in self.tier_statuses.items() if s == status])
                for status in TierStatus
            },
            "total_allocations": len(self.allocations),
            "average_load": (
                sum(self.tier_loads.values()) / len(self.tier_loads) if self.tier_loads else 0.0
            ),
        }
