"""
Aurora Auto-Evolution System
Phase 7 - Adaptive auto-evolution loop for Aurora-X
Runs daily or on-error evolution cycles to refine Supervisor + modules.
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
    """

    def __init__(self, supervisor, knowledge_path=None):
        self.supervisor = supervisor
        self.knowledge_path = Path(knowledge_path or "aurora_supervisor/data/knowledge/models/state_snapshot.json")
        self.log_path = Path("aurora_supervisor/data/knowledge/models/evolution_log.jsonl")
        self.last_run = None
        self.security_levels = {
            "minor": self._apply_direct,
            "moderate": self._apply_safe,
            "critical": self._request_core_validation
        }
        self._thread = threading.Thread(target=self._background_loop, daemon=True, name="AutoEvolution")
        self._running = False

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

    def _apply_direct(self, improvement):
        print(f"[AutoEvolution] Applying direct improvement -> {improvement['target']} (+{improvement['delta']})")
        self.supervisor.update_parameter(improvement["target"], improvement["delta"])

    def _apply_safe(self, improvement):
        print(f"[AutoEvolution] Safe improvement (moderate) queued -> {improvement['target']}")
        self.supervisor.queue_safe_update(improvement)

    def _request_core_validation(self, improvement):
        print(f"[AutoEvolution] Critical improvement detected -> {improvement['target']} requires core validation")
        try:
            self.supervisor.request_core_validation(improvement)
        except Exception as e:
            print("[AutoEvolution] Core validation failed:", e)
