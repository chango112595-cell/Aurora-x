"""
Aurora-X Autonomy Manager
Manages hybrid/autonomy policies and autonomous operation modes.
"""

import logging
import time
import threading
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class AutonomyLevel(Enum):
    """Autonomy operation levels."""
    DISABLED = 0
    SUPERVISED = 1
    HYBRID = 2
    AUTONOMOUS = 3
    FULL_AUTO = 4


class ActionType(Enum):
    """Types of autonomous actions."""
    MONITOR = "monitor"
    DIAGNOSE = "diagnose"
    REPAIR = "repair"
    OPTIMIZE = "optimize"
    GENERATE = "generate"
    DEPLOY = "deploy"
    ROLLBACK = "rollback"


@dataclass
class AutonomyPolicy:
    """Policy configuration for autonomy operations."""
    level: AutonomyLevel = AutonomyLevel.HYBRID
    allowed_actions: List[ActionType] = field(default_factory=lambda: [
        ActionType.MONITOR, ActionType.DIAGNOSE
    ])
    require_approval: List[ActionType] = field(default_factory=lambda: [
        ActionType.DEPLOY, ActionType.ROLLBACK
    ])
    max_auto_repairs_per_hour: int = 10
    max_auto_optimizations_per_day: int = 5
    cooldown_seconds: int = 60
    notification_channels: List[str] = field(default_factory=list)
    audit_all_actions: bool = True
    sandbox_new_changes: bool = True


@dataclass
class AutonomyAction:
    """Represents an autonomous action."""
    action_id: str
    action_type: ActionType
    target: str
    payload: Dict[str, Any]
    timestamp: float
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    approved_by: Optional[str] = None
    executed_at: Optional[float] = None


class AutonomyManager:
    """
    Manages autonomous operations with policy enforcement.
    Supports hybrid mode where some actions require approval.
    """
    
    def __init__(self, policy: Optional[AutonomyPolicy] = None):
        self.policy = policy or AutonomyPolicy()
        self.action_queue: List[AutonomyAction] = []
        self.action_history: List[AutonomyAction] = []
        self.pending_approvals: Dict[str, AutonomyAction] = {}
        self._action_counts: Dict[str, int] = {}
        self._last_reset = time.time()
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=5)
        self._running = False
        self._action_handlers: Dict[ActionType, Callable] = {}
    
    def register_handler(self, action_type: ActionType, handler: Callable):
        """Register a handler for an action type."""
        self._action_handlers[action_type] = handler
        logger.info(f"Registered handler for {action_type.value}")
    
    def can_execute(self, action_type: ActionType) -> bool:
        """Check if action type is allowed under current policy."""
        if self.policy.level == AutonomyLevel.DISABLED:
            return False
        
        if action_type not in self.policy.allowed_actions:
            return False
        
        return True
    
    def requires_approval(self, action_type: ActionType) -> bool:
        """Check if action requires human approval."""
        if self.policy.level == AutonomyLevel.FULL_AUTO:
            return False
        
        if self.policy.level == AutonomyLevel.SUPERVISED:
            return True
        
        return action_type in self.policy.require_approval
    
    def check_rate_limits(self, action_type: ActionType) -> bool:
        """Check if action is within rate limits."""
        with self._lock:
            now = time.time()
            
            if now - self._last_reset > 3600:
                self._action_counts = {}
                self._last_reset = now
            
            key = action_type.value
            count = self._action_counts.get(key, 0)
            
            if action_type == ActionType.REPAIR:
                return count < self.policy.max_auto_repairs_per_hour
            elif action_type == ActionType.OPTIMIZE:
                return count < self.policy.max_auto_optimizations_per_day
            
            return True
    
    def submit_action(self, action_type: ActionType, target: str,
                      payload: Optional[Dict[str, Any]] = None) -> AutonomyAction:
        """Submit an action for execution or approval."""
        action_id = f"{action_type.value}_{int(time.time() * 1000)}"
        
        action = AutonomyAction(
            action_id=action_id,
            action_type=action_type,
            target=target,
            payload=payload or {},
            timestamp=time.time()
        )
        
        if not self.can_execute(action_type):
            action.status = "rejected"
            action.result = {"error": "Action not allowed by policy"}
            self.action_history.append(action)
            return action
        
        if not self.check_rate_limits(action_type):
            action.status = "rate_limited"
            action.result = {"error": "Rate limit exceeded"}
            self.action_history.append(action)
            return action
        
        if self.requires_approval(action_type):
            action.status = "pending_approval"
            self.pending_approvals[action_id] = action
            logger.info(f"Action {action_id} requires approval")
        else:
            self._queue_execution(action)
        
        return action
    
    def approve_action(self, action_id: str, approver: str) -> Optional[AutonomyAction]:
        """Approve a pending action."""
        if action_id not in self.pending_approvals:
            return None
        
        action = self.pending_approvals.pop(action_id)
        action.approved_by = approver
        action.status = "approved"
        
        self._queue_execution(action)
        return action
    
    def reject_action(self, action_id: str, reason: str) -> Optional[AutonomyAction]:
        """Reject a pending action."""
        if action_id not in self.pending_approvals:
            return None
        
        action = self.pending_approvals.pop(action_id)
        action.status = "rejected"
        action.result = {"reason": reason}
        self.action_history.append(action)
        return action
    
    def _queue_execution(self, action: AutonomyAction):
        """Queue action for execution."""
        action.status = "queued"
        self.action_queue.append(action)
        
        if self._running:
            self._executor.submit(self._execute_action, action)
    
    def _execute_action(self, action: AutonomyAction):
        """Execute an action."""
        try:
            action.status = "executing"
            action.executed_at = time.time()
            
            handler = self._action_handlers.get(action.action_type)
            
            if handler:
                result = handler(action.target, action.payload)
                action.result = result
                action.status = "completed"
            else:
                action.result = {"status": "no_handler"}
                action.status = "completed"
            
            with self._lock:
                key = action.action_type.value
                self._action_counts[key] = self._action_counts.get(key, 0) + 1
            
        except Exception as e:
            action.status = "failed"
            action.result = {"error": str(e)}
            logger.error(f"Action {action.action_id} failed: {e}")
        
        finally:
            self.action_history.append(action)
            if action in self.action_queue:
                self.action_queue.remove(action)
    
    def start(self):
        """Start the autonomy manager."""
        self._running = True
        logger.info("Autonomy manager started")
        
        for action in self.action_queue:
            self._executor.submit(self._execute_action, action)
    
    def stop(self):
        """Stop the autonomy manager."""
        self._running = False
        self._executor.shutdown(wait=True)
        logger.info("Autonomy manager stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current autonomy status."""
        return {
            "running": self._running,
            "policy_level": self.policy.level.name,
            "queued_actions": len(self.action_queue),
            "pending_approvals": len(self.pending_approvals),
            "action_history_count": len(self.action_history),
            "action_counts": dict(self._action_counts),
            "allowed_actions": [a.value for a in self.policy.allowed_actions]
        }
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get list of actions pending approval."""
        return [
            {
                "action_id": a.action_id,
                "type": a.action_type.value,
                "target": a.target,
                "timestamp": a.timestamp
            }
            for a in self.pending_approvals.values()
        ]
    
    def set_policy(self, policy: AutonomyPolicy):
        """Update the autonomy policy."""
        self.policy = policy
        logger.info(f"Policy updated to level: {policy.level.name}")
    
    def escalate_to_full_auto(self, duration_seconds: int = 3600):
        """Temporarily escalate to full autonomous mode."""
        original_level = self.policy.level
        self.policy.level = AutonomyLevel.FULL_AUTO
        
        def restore():
            time.sleep(duration_seconds)
            self.policy.level = original_level
            logger.info(f"Restored autonomy level to {original_level.name}")
        
        threading.Thread(target=restore, daemon=True).start()
        logger.warning(f"Escalated to FULL_AUTO for {duration_seconds}s")
