"""
Aurora Auto-Evolution System
Phase 7 - Adaptive auto-evolution loop for Aurora-X
Runs daily or on-error evolution cycles to refine Supervisor + modules.
Includes review queue for core/foundation changes requiring manual approval.
"""
from pathlib import Path
import json
import time
import threading
import random
import datetime


class AutoEvolution:
    """
    Adaptive auto-evolution manager for Aurora-X.
    Runs daily or on-error evolution cycles to refine Supervisor + modules.
    Applies safe optimizations automatically, escalates core changes
    through Aurora's internal safety layer.
    
    Safety Features:
    - Minor/moderate changes: auto-applied
    - Core/foundation/kernel changes: queued for manual approval
    - Full audit trail in evolution_log.jsonl
    """

    CORE_KEYWORDS = ("core", "foundation", "kernel", "aurora_nexus", "memory_fabric", "nexus")

    def __init__(self, supervisor, knowledge_path=None):
        self.supervisor = supervisor
        self.knowledge_path = Path(knowledge_path or "aurora_supervisor/data/knowledge/models/state_snapshot.json")
        self.log_path = Path("aurora_supervisor/data/knowledge/models/evolution_log.jsonl")
        self.last_run = None
        self.review_queue = []
        self.security_levels = {
            "minor": self._apply_direct,
            "moderate": self._apply_safe,
            "critical": self._request_core_validation
        }
        self._thread = threading.Thread(target=self._background_loop, daemon=True, name="AutoEvolution")
        self._running = False
        self._load_review_queue()

    def start(self):
        print("[AutoEvolution] Starting adaptive evolution loop ...")
        self._running = True
        self._thread.start()

    def stop(self):
        print("[AutoEvolution] Stopping evolution loop ...")
        self._running = False

    def _background_loop(self):
        while self._running:
            try:
                now = time.time()
                if self.last_run is None or (now - self.last_run) > 86400:
                    self.run_evolution_cycle(reason="daily")
                if self.supervisor.detect_instability():
                    self.run_evolution_cycle(reason="instability")
            except Exception as e:
                print("[AutoEvolution] Exception in background loop:", e)
            time.sleep(300)

    def run_evolution_cycle(self, reason="manual"):
        self.last_run = time.time()
        print(f"[AutoEvolution] Starting evolution cycle ({reason}) at {datetime.datetime.now()}")

        try:
            data = json.loads(self.knowledge_path.read_text())
        except Exception as e:
            print("[AutoEvolution] Could not load knowledge snapshot:", e)
            return

        improvements = self._analyze_and_generate_improvements(data)
        for item in improvements:
            level = item.get("level", "minor")
            handler = self.security_levels.get(level, self._apply_safe)
            handler(item)

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a") as log:
            log.write(json.dumps({
                "timestamp": datetime.datetime.now().isoformat(),
                "reason": reason,
                "improvements": improvements
            }) + "\n")

        print(f"[AutoEvolution] Completed evolution cycle with {len(improvements)} improvements.")

    def _analyze_and_generate_improvements(self, data):
        """
        Evaluate performance/health metrics and propose improvements.
        """
        improvements = []
        metrics = data.get("metrics", {})
        for key, val in metrics.items():
            if isinstance(val, (int, float)) and val < 0.8:
                level = "minor"
                if "core" in key:
                    level = "critical"
                elif "nexus" in key or "healer" in key:
                    level = "moderate"
                improvements.append({
                    "target": key,
                    "proposed": f"optimize_{key}",
                    "delta": round(random.uniform(0.01, 0.1), 4),
                    "level": level
                })
        
        memory = data.get("memory", {})
        worker_count = len([k for k in memory.keys() if k.startswith("task-")])
        healer_count = len([k for k in memory.keys() if k.startswith("healer-")])
        
        if worker_count > 0 and healer_count > 0:
            efficiency = healer_count / (worker_count + healer_count)
            if efficiency < 0.2:
                improvements.append({
                    "target": "healer_ratio",
                    "proposed": "increase_healer_allocation",
                    "delta": 0.05,
                    "level": "moderate"
                })
        
        return improvements

    def _load_review_queue(self):
        """Load pending review items from evolution log"""
        if not self.log_path.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self.log_path.write_text("")
            return
        try:
            for line in self.log_path.read_text().splitlines():
                if not line.strip():
                    continue
                entry = json.loads(line)
                for item in entry.get("queued", []):
                    if item.get("requires_approval") and item not in self.review_queue:
                        self.review_queue.append(item)
        except Exception as e:
            print(f"[AutoEvolution] Could not load review queue: {e}")

    def _is_core_change(self, target):
        """Check if target involves core/foundation components"""
        target_lower = target.lower()
        return any(kw in target_lower for kw in self.CORE_KEYWORDS)

    def _apply_direct(self, improvement):
        """Apply minor improvements directly"""
        target = improvement.get("target", "")
        if self._is_core_change(target):
            self._queue_for_approval(improvement)
            return
        print(f"[AutoEvolution] Applying direct improvement -> {target} (+{improvement.get('delta', 0)})")
        if hasattr(self.supervisor, 'update_parameter'):
            self.supervisor.update_parameter(target, improvement.get("delta", 0))

    def _apply_safe(self, improvement):
        """Queue moderate improvements safely"""
        target = improvement.get("target", "")
        if self._is_core_change(target):
            self._queue_for_approval(improvement)
            return
        print(f"[AutoEvolution] Safe improvement (moderate) queued -> {target}")
        if hasattr(self.supervisor, 'queue_safe_update'):
            self.supervisor.queue_safe_update(improvement)

    def _request_core_validation(self, improvement):
        """Critical improvements always require approval"""
        print(f"[AutoEvolution] Critical improvement detected -> {improvement.get('target')} requires core validation")
        self._queue_for_approval(improvement)
        try:
            if hasattr(self.supervisor, 'request_core_validation'):
                self.supervisor.request_core_validation(improvement)
        except Exception as e:
            print("[AutoEvolution] Core validation failed:", e)

    def _queue_for_approval(self, improvement):
        """Add improvement to review queue for manual approval"""
        improvement["requires_approval"] = True
        improvement["queued_at"] = datetime.datetime.now().isoformat()
        if improvement not in self.review_queue:
            self.review_queue.append(improvement)
        print(f"[AutoEvolution] Queued for manual approval: {improvement.get('target')} (level={improvement.get('level')})")

    def daily_tick(self):
        """Called from supervisor heartbeat - runs evolution if 24h have passed"""
        if self.last_run is None or (time.time() - self.last_run) > 86400:
            print("[AutoEvolution] Running daily evolution cycle ...")
            self.run_evolution_cycle(reason="daily_tick")
        else:
            print("[AutoEvolution] Already evolved today.")

    def get_pending_approvals(self):
        """Return list of improvements waiting for manual approval"""
        return [item for item in self.review_queue if item.get("requires_approval")]

    def approve_improvement(self, target):
        """Approve and apply a queued improvement"""
        for item in self.review_queue:
            if item.get("target") == target and item.get("requires_approval"):
                print(f"[AutoEvolution] Approved and applying: {target}")
                item["requires_approval"] = False
                item["approved_at"] = datetime.datetime.now().isoformat()
                if hasattr(self.supervisor, 'update_parameter'):
                    self.supervisor.update_parameter(target, item.get("delta", 0))
                self.fabric_record_approval(item)
                return True
        print(f"[AutoEvolution] No pending approval found for: {target}")
        return False

    def reject_improvement(self, target, reason=""):
        """Reject a queued improvement"""
        for item in self.review_queue:
            if item.get("target") == target and item.get("requires_approval"):
                print(f"[AutoEvolution] Rejected: {target}")
                self.review_queue.remove(item)
                item["rejected"] = True
                item["rejection_reason"] = reason
                item["rejected_at"] = datetime.datetime.now().isoformat()
                self.fabric_record_approval(item)
                return True
        return False

    def fabric_record_approval(self, item):
        """Log approval/rejection to evolution log"""
        try:
            with self.log_path.open("a") as f:
                f.write(json.dumps({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "approval_decision",
                    "item": item
                }) + "\n")
        except Exception as e:
            print(f"[AutoEvolution] Failed to record approval: {e}")
