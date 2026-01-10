"""
Aurora Supervisor System
Phase 4–6 Mega Supervisor
Safe for Replit sandbox execution
"""

import json
import os
import platform
import queue
import shutil
import sys
import threading
import time
import traceback

import psutil

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

try:
    from aurora_core.utils import json_tools

    JSON_TOOLS_AVAILABLE = True
except ImportError:
    json_tools = None
    JSON_TOOLS_AVAILABLE = False


# ---------- KNOWLEDGE FABRIC (persistent memory) ----------
class KnowledgeFabric:
    def __init__(self, root="aurora_supervisor/data/knowledge"):
        self.root = root
        os.makedirs(root, exist_ok=True)
        self.events_log = os.path.join(root, "events.jsonl")
        self.models_dir = os.path.join(root, "models")
        os.makedirs(self.models_dir, exist_ok=True)
        self.memory = {}

    def record_event(self, kind, path, reason):
        event = {"ts": time.time(), "kind": kind, "path": path, "reason": reason}
        with open(self.events_log, "a") as f:
            f.write(json.dumps(event) + "\n")

    def save_state(self, name="state_snapshot"):
        path = os.path.join(self.models_dir, f"{name}.json")
        snapshot = {"timestamp": time.time(), "memory": self.memory}
        with open(path, "w") as f:
            json.dump(snapshot, f, indent=2)

    def load_state(self, name="state_snapshot"):
        path = os.path.join(self.models_dir, f"{name}.json")
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        print("[KnowledgeFabric] State file is empty, resetting")
                        self.memory = {}
                        return
                    data = json.loads(content)
                    self.memory = data.get("memory", {}) if isinstance(data, dict) else {}
                    print(f"[KnowledgeFabric] Loaded state with {len(self.memory)} memory entries")
            except json.JSONDecodeError as e:
                print(f"[KnowledgeFabric] State file corrupted (JSON error), regenerating: {e}")
                # Backup corrupted file
                backup_path = f"{path}.corrupted.{int(time.time())}"
                try:
                    import shutil

                    shutil.copy2(path, backup_path)
                    print(f"[KnowledgeFabric] Corrupted file backed up to {backup_path}")
                except Exception:
                    pass
                self.memory = {}
                # Regenerate valid snapshot
                self.save_state(name)
            except Exception as e:
                print(f"[KnowledgeFabric] State file error, resetting: {e}")
                self.memory = {}


# ---------- ENVIRONMENT ANALYSIS ----------
def analyze_environment():
    info = {
        "os": platform.system(),
        "version": platform.version(),
        "cpu_count": os.cpu_count(),
        "total_memory_gb": round(psutil.virtual_memory().total / 1e9, 2),
        "disk_free_gb": round(shutil.disk_usage("/").free / 1e9, 2),
    }
    print(f"[Supervisor] Environment scan: {info}")
    return info


# ---------- WORKER THREADS ----------
class BaseWorker(threading.Thread):
    def __init__(self, wid, role, task_q, fabric):
        super().__init__(daemon=True)
        self.wid = wid
        self.role = role
        self.q = task_q
        self.fabric = fabric
        self.active = True

    def run(self):
        while self.active:
            try:
                task = self.q.get(timeout=2)
                self.process(task)
            except queue.Empty:
                continue
            except Exception as e:
                self.fabric.record_event("error", f"{self.role}-{self.wid}", str(e))
                traceback.print_exc()

    def process(self, task):
        msg = f"[{self.role}-{self.wid}] processing task: {task}"
        print(msg)
        self.fabric.record_event("task", f"{self.role}-{self.wid}", msg)
        self.fabric.memory[f"{self.role}-{self.wid}"] = task

    def stop(self):
        self.active = False


# ---------- SUPERVISOR CORE ----------
class AuroraSupervisor:
    def __init__(self, root="aurora_supervisor"):
        self.root = root
        self.fabric = KnowledgeFabric(os.path.join(root, "data/knowledge"))
        self.heal_q = queue.Queue()
        self.task_q = queue.Queue()
        self.healers = []
        self.workers = []
        self.running = True
        self.fabric.load_state()
        self.parameters = {}
        self.pending_updates = []
        self.error_count = 0
        self.evolver = None
        self.json = json_tools
        if JSON_TOOLS_AVAILABLE:
            print("[Aurora Supervisor] Internal JSON Tools registered.")

    def start(self):
        analyze_environment()
        self.spawn_workers()
        self._start_auto_evolution()
        self.main_loop()

    def _start_auto_evolution(self):
        try:
            try:
                from aurora_supervisor.auto_evolution import AutoEvolution
            except ImportError:
                from auto_evolution import AutoEvolution
            self.evolver = AutoEvolution(supervisor=self)
            self.evolver.start()
        except Exception as e:
            print(f"[Supervisor] Auto-evolution init failed: {e}")

    def spawn_workers(self):
        for i in range(100):
            h = BaseWorker(i, "healer", self.heal_q, self.fabric)
            self.healers.append(h)
            h.start()
        for i in range(300):
            w = BaseWorker(i, "task", self.task_q, self.fabric)
            self.workers.append(w)
            w.start()
        print("[Supervisor] 400 workers operational (100 healers + 300 tasks).")

    def main_loop(self):
        try:
            while self.running:
                self.dispatch_health_tasks()
                self.fabric.save_state()
                time.sleep(15)
        except KeyboardInterrupt:
            self.shutdown()

    def dispatch_health_tasks(self):
        """Dispatch health tasks to healers - ensures heal queue is populated"""
        # Add various health check tasks to heal queue
        health_tasks = [
            "validate_integrity_phase_4_6",
            "check_system_health",
            "verify_module_integrity",
            "monitor_worker_health",
            "check_memory_fabric",
        ]
        import contextlib

        for task in health_tasks:
            with contextlib.suppress(queue.Full):
                self.heal_q.put(task, block=False)
        self.task_q.put("build_phase_4_6_modules")
        self.task_q.put("optimize_learning_parameters")

    def shutdown(self):
        print("[Supervisor] Shutting down...")
        self.running = False
        if self.evolver:
            self.evolver.stop()
        for h in self.healers + self.workers:
            h.stop()
        self.fabric.save_state()
        print("[Supervisor] State saved, all workers stopped.")

    def detect_instability(self):
        """Check if error logs exceed threshold"""
        try:
            events_file = os.path.join(self.root, "data/knowledge/events.jsonl")
            if not os.path.exists(events_file):
                return False
            recent_errors = 0
            cutoff = time.time() - 3600
            with open(events_file) as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        if event.get("kind") == "error" and event.get("ts", 0) > cutoff:
                            recent_errors += 1
                    except Exception:
                        continue
            return recent_errors > 5
        except Exception:
            return False

    def update_parameter(self, key, delta):
        """Apply local parameter adjustment"""
        self.parameters[key] = self.parameters.get(key, 1.0) + delta
        self.fabric.record_event("evolution", key, f"Parameter updated by {delta}")

    def queue_safe_update(self, improvement):
        """Queue a moderate improvement for safe application"""
        self.pending_updates.append(improvement)
        self.fabric.record_event("evolution", improvement.get("target"), "Queued for safe update")

    def request_core_validation(self, improvement):
        """Request core validation for critical improvements"""
        self.fabric.record_event(
            "evolution", improvement.get("target"), "Core validation requested"
        )
        print(f"[Supervisor] Core validation requested for: {improvement.get('target')}")

    def dispatch_task(self, task_name):
        """Dispatch a task to the task queue for worker processing"""
        self.task_q.put(task_name)
        self.fabric.record_event("dispatch", task_name, f"Task dispatched: {task_name}")
        print(f"[Supervisor] Dispatched task: {task_name}")

    def dispatch_heal(self, heal_task):
        """Dispatch a healing task to the healer queue"""
        self.heal_q.put(heal_task)
        self.fabric.record_event("heal", heal_task, f"Heal task dispatched: {heal_task}")

    def heal(self):
        """Trigger healers for error recovery"""
        self.heal_q.put("emergency_heal_cycle")
        self.heal_q.put("validate_system_integrity")
        self.heal_q.put("recover_failed_modules")
        self.fabric.record_event("heal", "emergency", "Emergency heal cycle triggered")
        print("[Supervisor] Emergency heal cycle triggered - 100 healers activated")

    def save_state(self, name="state_snapshot"):
        """Save current state to knowledge fabric"""
        self.fabric.memory["parameters"] = self.parameters
        self.fabric.memory["pending_updates"] = len(self.pending_updates)
        self.fabric.memory["error_count"] = self.error_count
        self.fabric.save_state(name)
        print(f"[Supervisor] State saved: {name}")

    def _load_knowledge(self):
        """Load previous state from knowledge fabric"""
        self.fabric.load_state()
        if "parameters" in self.fabric.memory:
            self.parameters = self.fabric.memory.get("parameters", {})
        print("[Supervisor] Knowledge loaded from fabric")

    def _spawn_workers(self):
        """Spawn worker threads if not already running"""
        if not self.workers:
            for i in range(300):
                w = BaseWorker(i, "task", self.task_q, self.fabric)
                self.workers.append(w)
                w.start()
            print("[Supervisor] 300 task workers spawned")

    def _spawn_healers(self):
        """Spawn healer threads if not already running"""
        if not self.healers:
            for i in range(100):
                h = BaseWorker(i, "healer", self.heal_q, self.fabric)
                self.healers.append(h)
                h.start()
            print("[Supervisor] 100 healers spawned")

    def get_status(self):
        """Get current supervisor status"""
        return {
            "running": self.running,
            "workers": len(self.workers),
            "healers": len(self.healers),
            "task_queue_size": self.task_q.qsize(),
            "heal_queue_size": self.heal_q.qsize(),
            "parameters": self.parameters,
            "error_count": self.error_count,
        }


SupervisorCore = AuroraSupervisor

if __name__ == "__main__":
    sup = AuroraSupervisor()
    sup.start()
