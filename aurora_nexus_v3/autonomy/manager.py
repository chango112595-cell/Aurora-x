"""
Aurora-X Autonomy Manager
Manages hybrid/autonomy policies and autonomous operation modes.
"""

import logging
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# Incident and RepairResult for prod_autonomy.py compatibility
@dataclass
class Incident:
    """Represents an incident that needs repair."""

    module_id: str
    error: str = ""
    stacktrace: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class RepairResult:
    """Result of a repair attempt."""

    success: bool = False
    promoted: bool = False
    attempts: int = 0
    details: dict[str, Any] = field(default_factory=dict)


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
    allowed_actions: list[ActionType] = field(
        default_factory=lambda: [ActionType.MONITOR, ActionType.DIAGNOSE]
    )
    require_approval: list[ActionType] = field(
        default_factory=lambda: [ActionType.DEPLOY, ActionType.ROLLBACK]
    )
    max_auto_repairs_per_hour: int = 10
    max_auto_optimizations_per_day: int = 5
    cooldown_seconds: int = 60
    notification_channels: list[str] = field(default_factory=list)
    audit_all_actions: bool = True
    sandbox_new_changes: bool = True


@dataclass
class AutonomyAction:
    """Represents an autonomous action."""

    action_id: str
    action_type: ActionType
    target: str
    payload: dict[str, Any]
    timestamp: float
    status: str = "pending"
    result: dict[str, Any] | None = None
    approved_by: str | None = None
    executed_at: float | None = None


class AutonomyManager:
    """
    Manages autonomous operations with policy enforcement.
    Supports hybrid mode where some actions require approval.
    """

    def __init__(
        self,
        policy: AutonomyPolicy | None = None,
        # New parameters for prod_autonomy.py compatibility
        manifest_registry: dict[str, Any] | None = None,
        autonomy_level: str = "balanced",
        hybrid_mode: bool = True,
        protected_scopes: list[str] | None = None,
        generator_func: Callable | None = None,
        inspector_func: Callable | None = None,
        sandbox_tester: Callable | None = None,
        promote_func: Callable | None = None,
        snapshot_func: Callable | None = None,
        restore_snapshot: Callable | None = None,
        notify_human: Callable | None = None,
        sign_artifact: Callable | None = None,
        max_repair_attempts: int = 3,
        worker_pool: int = 6,
    ):
        self.policy = policy or AutonomyPolicy()
        self.action_queue: list[AutonomyAction] = []
        self.action_history: list[AutonomyAction] = []
        self.pending_approvals: dict[str, AutonomyAction] = {}
        self._action_counts: dict[str, int] = {}
        self._last_reset = time.time()
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=worker_pool)
        self._running = False
        self._action_handlers: dict[ActionType, Callable] = {}

        # Store prod_autonomy adapters
        self.manifest_registry = manifest_registry or {}
        self.autonomy_level = autonomy_level
        self.hybrid_mode = hybrid_mode
        self.protected_scopes = protected_scopes or []
        self.generator_func = generator_func
        self.inspector_func = inspector_func
        self.sandbox_tester = sandbox_tester
        self.promote_func = promote_func
        self.snapshot_func = snapshot_func
        self.restore_snapshot = restore_snapshot
        self.notify_human = notify_human
        self.sign_artifact = sign_artifact
        self.max_repair_attempts = max_repair_attempts

    def handle_incident(self, incident: Incident) -> RepairResult:
        """
        Handle an incident by attempting to repair the affected module.
        This is the main entry point for prod_autonomy.py.
        """
        result = RepairResult()
        module_id = incident.module_id

        logger.info(f"Handling incident for module: {module_id}")

        # Check if module is protected
        if module_id in self.protected_scopes:
            logger.warning(f"Module {module_id} is protected, notifying human")
            if self.notify_human:
                self.notify_human({"incident": incident.__dict__, "reason": "protected_scope"})
            result.details = {"reason": "protected_scope"}
            return result

        # Get manifest for the module
        manifest = self.manifest_registry.get(module_id, {"id": module_id})

        for attempt in range(1, self.max_repair_attempts + 1):
            result.attempts = attempt
            logger.info(f"Repair attempt {attempt}/{self.max_repair_attempts} for {module_id}")

            try:
                # Step 1: Generate candidate
                if self.generator_func:
                    candidate_path = self.generator_func(manifest)
                else:
                    result.details = {"error": "no_generator_func"}
                    break

                # Step 2: Inspect candidate
                if self.inspector_func:
                    inspect_result = self.inspector_func(candidate_path)
                    if not inspect_result.get("ok"):
                        logger.warning(f"Inspection failed: {inspect_result.get('issues')}")
                        continue

                # Step 3: Test in sandbox
                if self.sandbox_tester:
                    test_inputs = manifest.get("test_inputs", [{}])
                    test_result = self.sandbox_tester(candidate_path, manifest, test_inputs)
                    if not test_result.get("ok"):
                        logger.warning(f"Sandbox test failed: {test_result}")
                        continue

                # Step 4: Promote if tests pass
                if self.promote_func:
                    promote_result = self.promote_func(candidate_path, manifest)
                    if promote_result.get("ok"):
                        result.success = True
                        result.promoted = True
                        result.details = promote_result
                        logger.info(f"Successfully repaired and promoted module {module_id}")
                        return result
                    else:
                        logger.warning(f"Promotion failed: {promote_result}")

            except Exception as e:
                logger.exception(f"Repair attempt {attempt} failed with exception: {e}")
                result.details = {"error": str(e), "attempt": attempt}

        # All attempts failed, notify human if in hybrid mode
        if self.hybrid_mode and self.notify_human:
            self.notify_human(
                {
                    "incident": incident.__dict__,
                    "attempts": result.attempts,
                    "reason": "max_attempts_exceeded",
                }
            )

        return result

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

    def submit_action(
        self, action_type: ActionType, target: str, payload: dict[str, Any] | None = None
    ) -> AutonomyAction:
        """Submit an action for execution or approval."""
        action_id = f"{action_type.value}_{int(time.time() * 1000)}"

        action = AutonomyAction(
            action_id=action_id,
            action_type=action_type,
            target=target,
            payload=payload or {},
            timestamp=time.time(),
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

    def approve_action(self, action_id: str, approver: str) -> AutonomyAction | None:
        """Approve a pending action."""
        if action_id not in self.pending_approvals:
            return None

        action = self.pending_approvals.pop(action_id)
        action.approved_by = approver
        action.status = "approved"

        self._queue_execution(action)
        return action

    def reject_action(self, action_id: str, reason: str) -> AutonomyAction | None:
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

    def get_status(self) -> dict[str, Any]:
        """Get current autonomy status."""
        return {
            "running": self._running,
            "policy_level": self.policy.level.name,
            "queued_actions": len(self.action_queue),
            "pending_approvals": len(self.pending_approvals),
            "action_history_count": len(self.action_history),
            "action_counts": dict(self._action_counts),
            "allowed_actions": [a.value for a in self.policy.allowed_actions],
        }

    def get_pending_approvals(self) -> list[dict[str, Any]]:
        """Get list of actions pending approval."""
        return [
            {
                "action_id": a.action_id,
                "type": a.action_type.value,
                "target": a.target,
                "timestamp": a.timestamp,
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


class AutonomyHTTPServer:
    """Simple HTTP server for health checks and metrics."""

    def __init__(self, manager: AutonomyManager, port: int = 8081):
        self.manager = manager
        self.port = port
        self._server = None

    def start(self):
        """Start the HTTP server."""
        import json
        from http.server import BaseHTTPRequestHandler, HTTPServer

        manager = self.manager

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"status":"healthy"}')
                elif self.path == "/ready":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"status":"ready"}')
                elif self.path == "/status":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(manager.get_status()).encode())
                elif self.path == "/metrics":
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    status = manager.get_status()
                    metrics = f"""# HELP aurora_autonomy_queued_actions Number of queued actions
# TYPE aurora_autonomy_queued_actions gauge
aurora_autonomy_queued_actions {status["queued_actions"]}
# HELP aurora_autonomy_pending_approvals Number of pending approvals
# TYPE aurora_autonomy_pending_approvals gauge
aurora_autonomy_pending_approvals {status["pending_approvals"]}
# HELP aurora_autonomy_history_count Total actions in history
# TYPE aurora_autonomy_history_count counter
aurora_autonomy_history_count {status["action_history_count"]}
"""
                    self.wfile.write(metrics.encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                logger.debug("Autonomy server: " + format, *args)

        self._server = HTTPServer(("0.0.0.0", self.port), Handler)
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        logger.info(f"Autonomy HTTP server started on port {self.port}")

    def stop(self):
        """Stop the HTTP server."""
        if self._server:
            self._server.shutdown()


def main():
    """CLI entrypoint for the autonomy manager."""
    import os
    import signal

    logging.basicConfig(
        level=getattr(logging, os.environ.get("AURORA_LOG_LEVEL", "INFO")),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting Aurora-X Autonomy Manager...")

    autonomy_level_str = os.environ.get("AURORA_AUTONOMY_LEVEL", "hybrid").upper()
    autonomy_level = (
        AutonomyLevel[autonomy_level_str]
        if autonomy_level_str in AutonomyLevel.__members__
        else AutonomyLevel.HYBRID
    )

    policy = AutonomyPolicy(
        level=autonomy_level,
        allowed_actions=[ActionType.MONITOR, ActionType.DIAGNOSE, ActionType.REPAIR],
        max_auto_repairs_per_hour=20,
    )

    manager = AutonomyManager(policy)

    http_port = int(os.environ.get("AURORA_AUTONOMY_PORT", "8081"))
    http_server = AutonomyHTTPServer(manager, http_port)
    http_server.start()

    manager.start()
    logger.info(f"Autonomy Manager running with level: {autonomy_level.name}")

    shutdown = threading.Event()

    def signal_handler(sig, frame):
        logger.info("Received shutdown signal...")
        shutdown.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        shutdown.wait()
    finally:
        logger.info("Shutting down...")
        http_server.stop()
        manager.stop()
        logger.info("Aurora-X Autonomy Manager stopped")


if __name__ == "__main__":
    main()
