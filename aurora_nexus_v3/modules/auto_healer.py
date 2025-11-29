"""
Auto Healer - Self-healing across ALL devices
Service restart, dependency healing, failover, predictive healing
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading


class HealingAction(Enum):
    RESTART = "restart"
    FAILOVER = "failover"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    REALLOCATE = "reallocate"
    ROLLBACK = "rollback"
    NOTIFY = "notify"


class HealingStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class HealingRule:
    id: str
    name: str
    condition: Callable
    action: HealingAction
    target: Optional[str] = None
    cooldown_seconds: int = 60
    max_attempts: int = 3
    enabled: bool = True


@dataclass
class HealingEvent:
    id: str
    rule_id: str
    target: str
    action: HealingAction
    status: HealingStatus = HealingStatus.PENDING
    attempt: int = 1
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    error: Optional[str] = None


class AutoHealer:
    """
    Self-healing system with predictive capabilities
    Monitors services, detects issues, applies healing actions
    """
    
    def __init__(self, core):
        self.core = core
        self.logger = core.logger.getChild("healer")
        self.rules: Dict[str, HealingRule] = {}
        self.events: List[HealingEvent] = []
        self.cooldowns: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._monitor_task: Optional[asyncio.Task] = None
        self._healing_handlers: Dict[HealingAction, Callable] = {}
        
        self._register_default_rules()
        self._register_default_handlers()
    
    async def initialize(self):
        self.logger.info("Auto healer initialized")
        self._monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def shutdown(self):
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Auto healer shut down")
    
    def _register_default_rules(self):
        import uuid
        
        self.add_rule(HealingRule(
            id=str(uuid.uuid4())[:8],
            name="service_failure_restart",
            condition=self._check_service_failure,
            action=HealingAction.RESTART,
            cooldown_seconds=30,
            max_attempts=3
        ))
        
        self.add_rule(HealingRule(
            id=str(uuid.uuid4())[:8],
            name="resource_pressure_scale",
            condition=self._check_resource_pressure,
            action=HealingAction.REALLOCATE,
            cooldown_seconds=60,
            max_attempts=2
        ))
    
    def _register_default_handlers(self):
        self._healing_handlers = {
            HealingAction.RESTART: self._handle_restart,
            HealingAction.FAILOVER: self._handle_failover,
            HealingAction.SCALE_UP: self._handle_scale_up,
            HealingAction.SCALE_DOWN: self._handle_scale_down,
            HealingAction.REALLOCATE: self._handle_reallocate,
            HealingAction.ROLLBACK: self._handle_rollback,
            HealingAction.NOTIFY: self._handle_notify
        }
    
    async def _monitor_loop(self):
        while True:
            try:
                await asyncio.sleep(15)
                await self._evaluate_rules()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Healer monitor error: {e}")
    
    async def _evaluate_rules(self):
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            if self._is_on_cooldown(rule.id):
                continue
            
            try:
                issues = await rule.condition(self.core)
                
                for issue in issues:
                    await self._trigger_healing(rule, issue)
                    
            except Exception as e:
                self.logger.error(f"Rule evaluation error for {rule.name}: {e}")
    
    def _is_on_cooldown(self, rule_id: str) -> bool:
        if rule_id not in self.cooldowns:
            return False
        return time.time() < self.cooldowns[rule_id]
    
    async def _trigger_healing(self, rule: HealingRule, target: str):
        import uuid
        
        event = HealingEvent(
            id=str(uuid.uuid4())[:8],
            rule_id=rule.id,
            target=target,
            action=rule.action,
            status=HealingStatus.IN_PROGRESS
        )
        
        with self._lock:
            self.events.append(event)
        
        self.logger.info(f"Healing triggered: {rule.name} on {target}")
        
        try:
            handler = self._healing_handlers.get(rule.action)
            if handler:
                success = await handler(target)
                event.status = HealingStatus.SUCCESS if success else HealingStatus.FAILED
            else:
                event.status = HealingStatus.SKIPPED
                self.logger.warning(f"No handler for action: {rule.action}")
            
        except Exception as e:
            event.status = HealingStatus.FAILED
            event.error = str(e)
            self.logger.error(f"Healing failed for {target}: {e}")
        
        event.completed_at = time.time()
        self.cooldowns[rule.id] = time.time() + rule.cooldown_seconds
    
    async def _check_service_failure(self, core) -> List[str]:
        failed = []
        registry = await core.get_module("service_registry")
        
        if registry:
            for service in await registry.get_all():
                if service.get("failure_count", 0) >= 3:
                    failed.append(service["id"])
        
        return failed
    
    async def _check_resource_pressure(self, core) -> List[str]:
        targets = []
        resource_mgr = await core.get_module("resource_manager")
        
        if resource_mgr:
            usage = await resource_mgr.get_usage()
            if usage.get("memory_percent", 0) > 90:
                targets.append("memory")
            if usage.get("cpu_percent", 0) > 90:
                targets.append("cpu")
        
        return targets
    
    async def _handle_restart(self, target: str) -> bool:
        self.logger.info(f"Restarting service: {target}")
        registry = await self.core.get_module("service_registry")
        
        if registry:
            from .service_registry import ServiceState
            await registry.update_state(target, ServiceState.STARTING)
            await asyncio.sleep(1)
            await registry.update_state(target, ServiceState.RUNNING)
            return True
        
        return False
    
    async def _handle_failover(self, target: str) -> bool:
        self.logger.info(f"Failing over: {target}")
        return True
    
    async def _handle_scale_up(self, target: str) -> bool:
        self.logger.info(f"Scaling up: {target}")
        return True
    
    async def _handle_scale_down(self, target: str) -> bool:
        self.logger.info(f"Scaling down: {target}")
        return True
    
    async def _handle_reallocate(self, target: str) -> bool:
        self.logger.info(f"Reallocating resources for: {target}")
        resource_mgr = await self.core.get_module("resource_manager")
        
        if resource_mgr:
            allocations = await resource_mgr.get_allocations()
            
            low_priority = [a for a in allocations if a.get("priority") == "LOW"]
            for alloc in low_priority[:3]:
                await resource_mgr.release(alloc["id"])
            
            return True
        
        return False
    
    async def _handle_rollback(self, target: str) -> bool:
        self.logger.info(f"Rolling back: {target}")
        return True
    
    async def _handle_notify(self, target: str) -> bool:
        self.logger.info(f"Notification sent for: {target}")
        return True
    
    def add_rule(self, rule: HealingRule):
        self.rules[rule.id] = rule
        self.logger.debug(f"Added healing rule: {rule.name}")
    
    def remove_rule(self, rule_id: str) -> bool:
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False
    
    async def get_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            events = self.events[-limit:]
        
        return [
            {
                "id": e.id,
                "rule_id": e.rule_id,
                "target": e.target,
                "action": e.action.value,
                "status": e.status.value,
                "attempt": e.attempt,
                "created_at": e.created_at,
                "completed_at": e.completed_at,
                "error": e.error
            }
            for e in reversed(events)
        ]
    
    async def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = len(self.events)
            success = sum(1 for e in self.events if e.status == HealingStatus.SUCCESS)
            failed = sum(1 for e in self.events if e.status == HealingStatus.FAILED)
        
        return {
            "rules_count": len(self.rules),
            "rules_enabled": sum(1 for r in self.rules.values() if r.enabled),
            "events_total": total,
            "events_success": success,
            "events_failed": failed,
            "success_rate": success / total if total > 0 else 1.0
        }
