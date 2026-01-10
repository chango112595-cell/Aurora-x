"""
Worker Multi-Agent Collaboration System
Self-contained collaboration framework for workers to share knowledge and coordinate
No external APIs - uses message passing, shared memory, and consensus algorithms
"""

import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CollaborationType(Enum):
    """Types of collaboration"""

    KNOWLEDGE_SHARING = "knowledge_sharing"
    TASK_DELEGATION = "task_delegation"
    PROBLEM_SOLVING = "problem_solving"
    RESOURCE_SHARING = "resource_sharing"
    CONSENSUS = "consensus"


class MessageType(Enum):
    """Types of messages"""

    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"


@dataclass
class CollaborationMessage:
    """A message between workers"""

    message_id: str
    sender_id: str
    receiver_id: str | None  # None for broadcast
    message_type: MessageType
    collaboration_type: CollaborationType
    content: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 5


@dataclass
class CollaborationSession:
    """A collaboration session"""

    session_id: str
    collaboration_type: CollaborationType
    participants: list[str]  # Worker IDs
    shared_knowledge: dict[str, Any]
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    outcome: dict[str, Any] | None = None


class WorkerCollaborationSystem:
    """
    Self-contained worker collaboration system
    Enables workers to collaborate, share knowledge, and coordinate
    """

    def __init__(self, worker_pool: Any = None):
        self.worker_pool = worker_pool
        self.message_queue: deque = deque(maxlen=10000)
        self.active_sessions: dict[str, CollaborationSession] = {}
        self.shared_knowledge_base: dict[str, Any] = {}
        self.worker_expertise: dict[str, list[str]] = {}  # worker_id -> [expertise_areas]
        self.collaboration_history: list[CollaborationSession] = []

    def send_message(
        self,
        sender_id: str,
        receiver_id: str | None,
        message_type: MessageType,
        collaboration_type: CollaborationType,
        content: dict[str, Any],
        priority: int = 5,
    ) -> CollaborationMessage:
        """Send a message between workers"""
        message = CollaborationMessage(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            collaboration_type=collaboration_type,
            content=content,
            priority=priority,
        )

        self.message_queue.append(message)

        # If receiver specified, deliver immediately
        if receiver_id and self.worker_pool:
            worker = self.worker_pool.get_worker(receiver_id)
            if worker:
                # Deliver message to worker
                if hasattr(worker, "receive_message"):
                    worker.receive_message(message)

        return message

    def broadcast_knowledge(self, sender_id: str, knowledge: dict[str, Any]):
        """Broadcast knowledge to all workers"""
        message = self.send_message(
            sender_id=sender_id,
            receiver_id=None,
            message_type=MessageType.BROADCAST,
            collaboration_type=CollaborationType.KNOWLEDGE_SHARING,
            content={"knowledge": knowledge},
            priority=3,
        )

        # Store in shared knowledge base
        for key, value in knowledge.items():
            self.shared_knowledge_base[key] = value

        return message

    def request_help(
        self,
        requester_id: str,
        problem: str,
        required_expertise: list[str] | None = None,
    ) -> CollaborationSession:
        """Request help from other workers"""
        session_id = str(uuid.uuid4())

        # Find workers with required expertise
        helpers = []
        if self.worker_pool and required_expertise:
            for worker_id, expertise in self.worker_expertise.items():
                if worker_id != requester_id:
                    if any(exp in expertise for exp in required_expertise):
                        helpers.append(worker_id)

        # If no specific expertise required, get available workers
        if not helpers and self.worker_pool:
            # Get first 3 available workers
            all_workers = (
                self.worker_pool.get_available_workers()
                if hasattr(self.worker_pool, "get_available_workers")
                else []
            )
            helpers = [w.worker_id for w in all_workers[:3] if w.worker_id != requester_id]

        # Create collaboration session
        session = CollaborationSession(
            session_id=session_id,
            collaboration_type=CollaborationType.PROBLEM_SOLVING,
            participants=[requester_id] + helpers,
            shared_knowledge={"problem": problem, "requester": requester_id},
        )

        self.active_sessions[session_id] = session

        # Send request messages
        for helper_id in helpers:
            self.send_message(
                sender_id=requester_id,
                receiver_id=helper_id,
                message_type=MessageType.REQUEST,
                collaboration_type=CollaborationType.PROBLEM_SOLVING,
                content={"problem": problem, "session_id": session_id},
                priority=7,
            )

        return session

    def delegate_task(
        self,
        delegator_id: str,
        task: Any,
        delegatee_id: str,
    ) -> CollaborationMessage:
        """Delegate a task to another worker"""
        return self.send_message(
            sender_id=delegator_id,
            receiver_id=delegatee_id,
            message_type=MessageType.REQUEST,
            collaboration_type=CollaborationType.TASK_DELEGATION,
            content={"task": task, "delegator": delegator_id},
            priority=8,
        )

    def reach_consensus(
        self,
        proposer_id: str,
        proposal: dict[str, Any],
        participants: list[str],
    ) -> dict[str, Any]:
        """Reach consensus among workers"""
        session_id = str(uuid.uuid4())

        # Create consensus session
        session = CollaborationSession(
            session_id=session_id,
            collaboration_type=CollaborationType.CONSENSUS,
            participants=participants,
            shared_knowledge={"proposal": proposal, "proposer": proposer_id},
        )

        self.active_sessions[session_id] = session

        # Send proposal to all participants
        votes = {}
        for participant_id in participants:
            if participant_id != proposer_id:
                self.send_message(
                    sender_id=proposer_id,
                    receiver_id=participant_id,
                    message_type=MessageType.REQUEST,
                    collaboration_type=CollaborationType.CONSENSUS,
                    content={"proposal": proposal, "session_id": session_id},
                    priority=9,
                )
                # Simulate vote (in real implementation, worker would respond)
                votes[participant_id] = True  # Assume approval

        # Calculate consensus
        approval_rate = len(votes) / len(participants) if participants else 0.0
        consensus_reached = approval_rate >= 0.5  # Simple majority

        session.outcome = {
            "consensus_reached": consensus_reached,
            "approval_rate": approval_rate,
            "votes": votes,
        }
        session.end_time = datetime.now()

        self.collaboration_history.append(session)
        del self.active_sessions[session_id]

        return session.outcome

    def share_resource(self, sharer_id: str, resource: dict[str, Any], recipients: list[str]):
        """Share a resource with other workers"""
        for recipient_id in recipients:
            self.send_message(
                sender_id=sharer_id,
                receiver_id=recipient_id,
                message_type=MessageType.NOTIFICATION,
                collaboration_type=CollaborationType.RESOURCE_SHARING,
                content={"resource": resource},
                priority=4,
            )

    def update_worker_expertise(self, worker_id: str, expertise: list[str]):
        """Update worker expertise"""
        self.worker_expertise[worker_id] = expertise

    def get_shared_knowledge(self, key: str) -> Any:
        """Get shared knowledge"""
        return self.shared_knowledge_base.get(key)

    def get_collaboration_stats(self) -> dict[str, Any]:
        """Get collaboration statistics"""
        return {
            "active_sessions": len(self.active_sessions),
            "total_messages": len(self.message_queue),
            "shared_knowledge_items": len(self.shared_knowledge_base),
            "total_collaborations": len(self.collaboration_history),
            "workers_with_expertise": len(self.worker_expertise),
        }
