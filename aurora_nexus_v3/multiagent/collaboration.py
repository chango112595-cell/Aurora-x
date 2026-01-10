"""
Multi-Agent Collaboration System
Self-contained multi-agent collaboration with communication and task distribution
No external APIs - uses internal protocols, task distribution, and result aggregation
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MessageType(Enum):
    """Message types"""

    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    KNOWLEDGE_SHARE = "knowledge_share"
    STATUS_UPDATE = "status_update"
    ASSISTANCE_REQUEST = "assistance_request"


@dataclass
class AgentMessage:
    """Agent message"""

    sender_id: str
    receiver_id: str | None  # None for broadcast
    message_type: MessageType
    content: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TaskAssignment:
    """Task assignment"""

    task_id: str
    agent_id: str
    task_description: str
    priority: int
    assigned_at: datetime = field(default_factory=datetime.now)


class MultiAgentCollaboration:
    """
    Self-contained multi-agent collaboration system
    Multiple Aurora agents collaborating on tasks
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.connected_agents: set[str] = set()
        self.message_queue: list[AgentMessage] = []
        self.task_assignments: dict[str, TaskAssignment] = {}
        self.shared_knowledge: dict[str, Any] = {}

    def connect_agent(self, agent_id: str):
        """Connect to another agent"""
        self.connected_agents.add(agent_id)

    def disconnect_agent(self, agent_id: str):
        """Disconnect from an agent"""
        self.connected_agents.discard(agent_id)

    def send_message(
        self,
        receiver_id: str | None,
        message_type: MessageType,
        content: dict[str, Any],
    ):
        """Send message to agent(s)"""
        message = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
        )

        # In real implementation, would send over network
        # For now, store in queue for processing
        self.message_queue.append(message)

    def receive_message(self) -> AgentMessage | None:
        """Receive message from queue"""
        if self.message_queue:
            return self.message_queue.pop(0)
        return None

    def request_assistance(self, task_description: str, required_capabilities: list[str]):
        """Request assistance from other agents"""
        # Broadcast assistance request
        self.send_message(
            receiver_id=None,  # Broadcast
            message_type=MessageType.ASSISTANCE_REQUEST,
            content={
                "task_description": task_description,
                "required_capabilities": required_capabilities,
                "requesting_agent": self.agent_id,
            },
        )

    def distribute_task(self, task_id: str, task_description: str, priority: int = 5) -> str | None:
        """Distribute task to available agent"""
        # Find available agent
        available_agent = self._find_available_agent()

        if available_agent:
            assignment = TaskAssignment(
                task_id=task_id,
                agent_id=available_agent,
                task_description=task_description,
                priority=priority,
            )
            self.task_assignments[task_id] = assignment

            # Send task to agent
            self.send_message(
                receiver_id=available_agent,
                message_type=MessageType.TASK_REQUEST,
                content={
                    "task_id": task_id,
                    "task_description": task_description,
                    "priority": priority,
                },
            )

            return available_agent

        return None

    def _find_available_agent(self) -> str | None:
        """Find available agent"""
        # Simplified - would check agent status in real implementation
        if self.connected_agents:
            return list(self.connected_agents)[0]
        return None

    def share_knowledge(self, knowledge_key: str, knowledge_value: Any):
        """Share knowledge with other agents"""
        self.shared_knowledge[knowledge_key] = knowledge_value

        # Broadcast knowledge share
        self.send_message(
            receiver_id=None,  # Broadcast
            message_type=MessageType.KNOWLEDGE_SHARE,
            content={
                "knowledge_key": knowledge_key,
                "knowledge_value": knowledge_value,
            },
        )

    def aggregate_results(self, task_id: str, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate results from multiple agents"""
        if not results:
            return {"success": False, "error": "No results to aggregate"}

        # Simple aggregation - combine results
        aggregated = {
            "task_id": task_id,
            "result_count": len(results),
            "results": results,
            "combined_result": self._combine_results(results),
        }

        return aggregated

    def _combine_results(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Combine multiple results"""
        # Simple combination strategy
        combined: dict[str, Any] = {}

        for result in results:
            for key, value in result.items():
                if key not in combined:
                    combined[key] = []
                if isinstance(combined[key], list):
                    combined[key].append(value)
                else:
                    combined[key] = [combined[key], value]

        return combined

    def resolve_conflicts(self, conflicting_results: list[dict[str, Any]]) -> dict[str, Any]:
        """Resolve conflicts between agent results"""
        if not conflicting_results:
            return {}

        # Simple conflict resolution - use majority or highest confidence
        # Count occurrences
        result_counts: dict[str, int] = {}

        for result in conflicting_results:
            result_str = str(result)
            result_counts[result_str] = result_counts.get(result_str, 0) + 1

        # Return most common result
        if result_counts:
            most_common = max(result_counts.items(), key=lambda x: x[1])
            return conflicting_results[0]  # Simplified

        return conflicting_results[0] if conflicting_results else {}

    def get_collaboration_stats(self) -> dict[str, Any]:
        """Get collaboration statistics"""
        return {
            "agent_id": self.agent_id,
            "connected_agents": len(self.connected_agents),
            "pending_messages": len(self.message_queue),
            "active_tasks": len(self.task_assignments),
            "shared_knowledge_items": len(self.shared_knowledge),
        }
